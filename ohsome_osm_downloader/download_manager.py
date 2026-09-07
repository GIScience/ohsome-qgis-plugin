import json

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsFeature,
    QgsWkbTypes,
    QgsBlockingNetworkRequest,
)

OHSOME_BASE_URL = "https://api.heigit.org/ohsome-api/v2-rc"

EXTRACTION_ENDPOINT = "extraction/features.parquet"


class OhsomeDownloadManager:
    """Handles building requests to the ohsome API extraction endpoint
    and converting GeoParquet responses into QGIS vector layers using
    GDAL's OGR Parquet driver.
    """

    def __init__(self, base_url: str = OHSOME_BASE_URL):
        self.base_url = base_url
        self._request_counter = 0

    def build_request_body(
        self,
        aoi: list[float],
        ohsome_filter: str,
        time,
        clip: bool = True,
        properties: list[str] | None = None,
    ) -> dict:
        """Build the JSON request body for the extraction endpoint call.

        :param aoi: bounding box as [west, south, east, north]
        :param ohsome_filter: raw ohsome filter string
        :param time: either a single ISO8601 string, "latest", or a dict
            with "start"/"end" keys for a time range
        :param clip: whether to clip geometries to the AOI
        :param properties: list of extra properties to request,
            e.g. ["tags", "metadata"]
        """
        body = {
            "filter": ohsome_filter,
            "aoi": aoi,
            "time": time,
            "clip": clip,
        }
        if properties:
            body["properties"] = properties
        return body

    def fetch_parquet_bytes(
        self, body: dict, api_key: str | None = None
    ) -> bytes:
        """Call the ohsome extraction endpoint and return the raw
        GeoParquet response bytes, using QgsBlockingNetworkRequest.

        :param api_key: optional ohsome API key, sent raw in the
            "authorization" header
        """
        url = f"{self.base_url}/{EXTRACTION_ENDPOINT}"

        request = QNetworkRequest(QUrl(url))
        request.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader,
            "application/json",
        )
        request.setRawHeader(b"accept", b"application/octet-stream")
        if api_key:
            request.setRawHeader(b"authorization", api_key.encode("utf-8"))

        payload = json.dumps(body).encode("utf-8")

        blocking_request = QgsBlockingNetworkRequest()
        error_code = blocking_request.post(request, payload)

        reply = blocking_request.reply()

        if error_code != QgsBlockingNetworkRequest.ErrorCode.NoError:
            content = bytes(reply.content())
            try:
                detail = json.loads(content.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                detail = content.decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Request failed ({blocking_request.errorMessage()}): "
                f"{detail}"
            )

        return bytes(reply.content())

    def parquet_bytes_to_layer(
        self, data: bytes, layer_name: str
    ) -> QgsVectorLayer:
        """Load GeoParquet bytes into a QgsVectorLayer via GDAL's
        virtual memory filesystem, avoiding any disk temp files.
        """
        from osgeo import gdal  # noqa: F401  (ensures GDAL bindings ready)

        driver = gdal.GetDriverByName("Parquet")
        if driver is None:
            raise RuntimeError(
                "GDAL's Parquet driver is not available in this "
                "installation. Run `ogrinfo --formats | grep -i parquet` "
                "to check, and rebuild/install GDAL with Arrow/Parquet "
                "support (libarrow, libparquet)."
            )

        self._request_counter += 1
        vsi_path = f"/vsimem/ohsome_extraction_{self._request_counter}.parquet"

        gdal.FileFromMemBuffer(vsi_path, data)

        layer = QgsVectorLayer(vsi_path, layer_name, "ogr")
        if not layer.isValid():
            gdal.Unlink(vsi_path)
            raise RuntimeError(
                f"Could not load layer '{layer_name}' from GeoParquet "
                "response. Ensure GDAL is built with Parquet/Arrow support."
            )
        return layer

    def split_layer_by_geometry_type(
        self, layer: QgsVectorLayer, layer_name: str
    ) -> list[QgsVectorLayer]:
        """Split a loaded layer into multiple memory layers grouped by
        geometry type (Point, LineString, Polygon, etc.).
        """
        geom_types: dict[int, list] = {}

        for feature in layer.getFeatures():
            geom = feature.geometry()
            if geom.isNull():
                continue
            wkb_type = geom.wkbType()
            geom_types.setdefault(wkb_type, []).append(feature)

        layers = []
        for wkb_type, features in geom_types.items():
            geom_name = QgsWkbTypes.displayString(wkb_type)
            sub_layer = QgsVectorLayer(
                f"{geom_name}?crs={layer.crs().authid()}",
                f"{layer_name}_{geom_name}",
                "memory",
            )
            provider = sub_layer.dataProvider()
            provider.addAttributes(layer.fields())
            sub_layer.updateFields()

            new_features = []
            for feature in features:
                new_feature = QgsFeature(sub_layer.fields())
                new_feature.setGeometry(feature.geometry())
                new_feature.setAttributes(feature.attributes())
                new_features.append(new_feature)

            provider.addFeatures(new_features)
            sub_layer.updateExtents()
            layers.append(sub_layer)
        return layers

    def split_layer_by_timestamp(
        self, layer: QgsVectorLayer, layer_name: str
    ) -> list[QgsVectorLayer]:
        """Split a loaded layer into multiple memory layers grouped by
        a timestamp/snapshot field, if one is found. Falls back to
        returning the original layer unmodified if no such field exists.
        """
        timestamp_field = self._find_timestamp_field(layer)
        if timestamp_field is None:
            return [layer]

        field_index = layer.fields().indexOf(timestamp_field)
        values = layer.uniqueValues(field_index)

        layers = []
        for value in sorted(values, key=str):
            sub_layer = QgsVectorLayer(
                f"{layer.wkbType()}?crs={layer.crs().authid()}",
                f"{layer_name}_{value}",
                "memory",
            )
            provider = sub_layer.dataProvider()
            provider.addAttributes(layer.fields())
            sub_layer.updateFields()

            matching_features = []
            for feature in layer.getFeatures():
                if feature[timestamp_field] != value:
                    continue
                new_feature = QgsFeature(sub_layer.fields())
                new_feature.setGeometry(feature.geometry())
                new_feature.setAttributes(feature.attributes())
                matching_features.append(new_feature)

            provider.addFeatures(matching_features)
            sub_layer.updateExtents()
            layers.append(sub_layer)
        return layers

    def _find_timestamp_field(self, layer: QgsVectorLayer) -> str | None:
        field_names = [f.name() for f in layer.fields()]
        for candidate in ("@snapshotTimestamp", "@timestamp", "snapshot"):
            if candidate in field_names:
                return candidate
        return None

    def add_layers_to_project(self, layers: list[QgsVectorLayer]) -> None:
        for layer in layers:
            QgsProject.instance().addMapLayer(layer)