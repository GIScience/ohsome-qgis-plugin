import json
from datetime import datetime
from qgis._core import QgsVectorLayer, QgsProcessingUtils, QgsProject
from ohsomeTools.common import client, request_core
from qgis.utils import iface


def processing_request(
    clnt, preferences, parameters, feedback, point_layer_preference={}
):
    try:
        request_time = datetime.now().strftime("%m-%d-%Y:%H-%M-%S")
        if len(point_layer_preference):
            result = clnt.request(
                f"/{preferences.get_request_url()}",
                {},
                post_json=point_layer_preference,
            )
        else:
            result = clnt.request(f"/metadata", {})
    except Exception as e:
        result = None

    if not result or not len(result):
        return False
    file = parameters["output"].replace(".file", ".csv")
    if "extractRegion" in result:
        vlayer: QgsVectorLayer = QgsVectorLayer(
            json.dumps(result.get("extractRegion").get("spatialExtent")),
            f"OHSOME_API_spatial_extent",
            "ogr",
        )
        QgsProject.instance().addMapLayer(vlayer)
        if vlayer:
            return True
    elif (
        all(i in result.keys() for i in ["type", "features"])
        and result.get("type").lower() == "featurecollection"
    ):
        # Process GeoJSON
        geojsons: [] = request_core.split_geojson_by_geometry(
            result,
            keep_geometry_less=parameters["check_keep_geometryless"],
            combine_single_with_multi_geometries=parameters[
                "check_merge_geometries"
            ],
        )
        for i in range(len(geojsons)):
            vlayer = request_core.create_ohsome_vector_layer(
                iface, geojsons[i], request_time, file
            )
            request_core.postprocess_metadata(geojsons[i], vlayer)
        return True
    elif "result" in result.keys() and len(result.get("result")) > 0:
        # Process flat tables
        header = result["result"][0].keys()
        vlayer = request_core.create_ohsome_csv_layer(
            iface,
            result["result"],
            header,
            file,
            request_time,
        )
        request_core.postprocess_metadata(result, vlayer)
        return True
    elif (
        "groupByResult" in result.keys()
        and len(result.get("groupByResult")) > 0
    ):
        # Process non-flat tables
        results = result["groupByResult"]
        for result_group in results:
            header = results[0]["result"][0].keys()
            vlayer = request_core.create_ohsome_csv_layer(
                iface,
                result_group["result"],
                header,
                file,
                request_time,
            )
            request_core.postprocess_metadata(result, vlayer)
        return True
    elif "ratioResult" in result.keys() and len(result.get("ratioResult")) > 0:
        # Process flat tables
        header = result.get("ratioResult")[0].keys()
        vlayer = request_core.create_ohsome_csv_layer(
            iface,
            result["ratioResult"],
            header,
            file,
            request_time,
        )
        request_core.postprocess_metadata(result, vlayer)
        return True
    feedback.reportError("Request Error")
