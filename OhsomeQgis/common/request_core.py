# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OhsomeQgis
                                 A QGIS plugin
 QGIS client to query the ohsome API
                              -------------------
        begin                : 2021-05-01
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Julian Psotta
        email                : julian.psotta@heigit.org
 ***************************************************************************/

 This plugin provides access to the ohsome API (https://api.ohsome.org),
 developed and maintained by the Heidelberg Institute for Geoinformation
 Technology, HeiGIT gGmbH, Heidelberg, Germany.
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import csv
import json
from datetime import datetime

from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QDialogButtonBox, QMessageBox
from qgis._core import (
    QgsVectorLayer,
    QgsVectorDataProvider,
    QgsTask,
    Qgis,
    QgsProcessingUtils,
    QgsLayerMetadata,
)

from qgis.core import (
    QgsFeature,
    QgsField,
)

from OhsomeQgis.common import client
from OhsomeQgis.utils import exceptions, logger
from OhsomeQgis.utils.exceptions import OhsomeBaseException


def postprocess_metadata(original_json: dict, vlayer: QgsVectorLayer):
    metadata: QgsLayerMetadata = vlayer.metadata()
    metadata.setTitle("Ohsome QGIS plugin query result.")
    if original_json.get("metadata") and original_json.get("metadata").get(
        "description"
    ):
        metadata.setAbstract(original_json.get("metadata").get("description"))
    if original_json.get("apiVersion"):
        metadata.addConstraint(
            QgsLayerMetadata.Constraint(
                f"{original_json.get('apiVersion')}", "apiVersion"
            )
        )
    if original_json.get("attribution"):
        attribution: dict = original_json.get("attribution")
        licenses: [] = [value for _, value in attribution.items()]
        metadata.setLicenses(licenses=licenses)
    vlayer.setMetadata(metadata=metadata)


def create_ohsome_csv_layer(
    iface, results, header, output_file, request_time: str
):
    with open(output_file, "w", newline="") as f:
        wr = csv.DictWriter(
            f,
            fieldnames=header,
        )
        wr.writeheader()
        for row_result in results:
            wr.writerow(row_result)
    return iface.addVectorLayer(
        output_file, f"ohsome_" f"{request_time}", "ogr"
    )


def create_ohsome_vector_layer(
    iface,
    geojson: dict,
    request_time: str,
    request_url: str,
    activate_temporal: bool = False,
):
    file = QgsProcessingUtils.generateTempFilename(f"{request_url}.geojson")
    with open(file, "w") as f:
        f.write(json.dumps(geojson, indent=4))
    vlayer: QgsVectorLayer = iface.addVectorLayer(
        file,
        f"ohsome_" f"{request_time}",
        "ogr",
    )
    postprocess_qgsvectorlayer(vlayer, activate_temporal=activate_temporal)
    return vlayer


def split_geojson_by_geometry(
    geojson: dict,
    return_features_per_geometry: bool = False,
    keep_geometry_less: bool = False,
    combine_single_with_multi_geometries: bool = False,
) -> [dict]:
    geojson_per_geometry = []
    features_per_geometry = {}
    if geojson.get("features"):
        features = geojson.pop("features")
    elif geojson.get("geometry") and geojson.get("geometry").get("geometries"):
        features = geojson.get("geometry").get("geometries")
    elif geojson.get("geometries") and len(geojson.get("geometries")):
        features = geojson.get("geometries")
    else:
        return {}
    for feature in features:
        try:
            if "geometry" in feature and feature["geometry"] is not None:
                geometry_type = feature["geometry"]["type"]
            elif "type" in feature and feature["type"] is not None:
                geometry_type = feature["type"]
            else:
                continue
            if geometry_type == "GeometryCollection":
                geometry_collection = split_geojson_by_geometry(
                    feature, return_features_per_geometry=True
                )
                return_features_per_geometry = False
                for feature_type in geometry_collection:
                    for sub_feature in geometry_collection[feature_type]:
                        sub_feature["properties"] = feature["properties"]
                    if feature_type not in features_per_geometry:
                        features_per_geometry[feature_type] = []
                    element: {}
                    features_per_geometry.get(feature_type).extend(
                        geometry_collection[feature_type]
                    )
                continue
            elif geometry_type not in features_per_geometry:
                features_per_geometry[geometry_type] = []
            features_per_geometry[geometry_type].append(feature)
        except Exception as err:
            raise exceptions.GeometryError(
                str("error"),
                f"Error constructing geometries from the GeoJSON response: {err}",
            )
    if return_features_per_geometry:
        return features_per_geometry
    if not keep_geometry_less and features_per_geometry.get("Feature"):
        features_per_geometry.pop("Feature")
    if combine_single_with_multi_geometries:
        if all(i in features_per_geometry for i in ["Polygon", "MultiPolygon"]):
            single_geometry = features_per_geometry.pop("Polygon")
            features_per_geometry.get("MultiPolygon").extend(single_geometry)
        if all(i in features_per_geometry for i in ["Point", "MultiPoint"]):
            single_geometry = features_per_geometry.pop("Point")
            features_per_geometry.get("MultiPoint").extend(single_geometry)
        if all(
            i in features_per_geometry
            for i in ["LineString", "MultiLineString"]
        ):
            single_geometry = features_per_geometry.pop("LineString")
            features_per_geometry.get("MultiLineString").extend(single_geometry)
    for _, feature_set in features_per_geometry.items():
        temp_geojson = geojson.copy()
        temp_geojson["features"] = feature_set
        geojson_per_geometry.append(temp_geojson)
        del temp_geojson

    return geojson_per_geometry


def postprocess_qgsvectorlayer(vlayer: QgsVectorLayer, activate_temporal: bool):
    if not vlayer or len(vlayer) <= 0:
        return
    # Determine the id field
    id_field = None
    if vlayer.fields().names().__contains__("@osmId"):
        id_field = "@osmId"
    # elif vlayer.fields().names().__contains__("id"):
    #     id_field = "id"
    else:
        return
    if vlayer.fields().names().__contains__("@validFrom"):
        date_start = "@validFrom"
        date_end = "@validTo"
    elif vlayer.fields().names().__contains__("@snapshotTimestamp"):
        date_start = "@snapshotTimestamp"
        date_end = "endDate"
    elif vlayer.fields().names().__contains__("@timestamp"):
        date_start = "@timestamp"
        date_end = "endDate"
    # elif vlayer.fields().names().__contains__("timestamp"):
    #     date_start = "timestamp"
    #     date_end = "endDate"
    else:
        return

    pr: QgsVectorDataProvider = vlayer.dataProvider()
    # changes are only possible when editing the layer
    vlayer.startEditing()
    if not vlayer.fields().names().__contains__(date_end):
        pr.addAttributes(
            [QgsField(date_end, QVariant.DateTime)]
        )  # Add durationsField
    vlayer.temporalProperties().setMode(2)  # Set the correct temporal mode
    vlayer.temporalProperties().setStartField(date_start)
    vlayer.temporalProperties().setEndField(date_end)
    vlayer.temporalProperties().setIsActive(activate_temporal)
    vlayer.commitChanges()
    vlayer.updateExtents()

    if date_end == "@validTo":
        features = sorted(
            vlayer.getFeatures(),
            key=lambda sort_timestamp: sort_timestamp[date_end],
        )
    else:
        features = sorted(
            vlayer.getFeatures(),
            key=lambda sort_timestamp: sort_timestamp[date_start],
        )
    youngest_timestamp = (
        features[-1].attribute(date_start) if len(features) > 0 else None
    )
    youngest_timestamp = youngest_timestamp.addDays(1)
    features = sorted(features, key=lambda sort_id: sort_id[id_field])
    vlayer.dataProvider().deleteFeatures([feature.id() for feature in features])
    for i in range(len(features) - 1):
        feature: QgsFeature = features[i]
        if (
            i < len(features) - 1
            and features[i + 1][id_field] == feature[id_field]
            and feature[date_end] is None
        ):
            feature.setAttribute(
                date_end, features[i + 1].attribute(date_start)
            )
        elif i < len(features) - 1 and feature[date_end] is not None:
            pass
        else:
            feature.setAttribute(date_end, youngest_timestamp)

    vlayer.dataProvider().addFeatures(features)

    vlayer.commitChanges()
    vlayer.updateExtents()


MESSAGE_CATEGORY = "RandomIntegerSumTask"


class ExtractionTaskFunction(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(
        self,
        iface,
        dlg,
        description: str,
        provider,
        request_url,
        preferences=None,
        activate_temporal: bool = False,
    ):
        super().__init__(description, QgsTask.CanCancel)
        self.iface = iface
        self.dlg = dlg
        self.total = 0
        self.iterations = 0
        self.exception = None
        self.request_url = request_url
        self.preferences = preferences if preferences is not None else {}
        self.activate_temporal = activate_temporal
        self.result: dict = {}
        self.exception: OhsomeBaseException = None
        self.request_time = None
        self.client = client.Client(provider)

    def postprocess_results(self) -> bool:
        if not self.result or not len(self.result):
            return False
        if "extractRegion" in self.result:
            vlayer: QgsVectorLayer = self.iface.addVectorLayer(
                json.dumps(
                    self.result.get("extractRegion").get("spatialExtent")
                ),
                f"OHSOME_API_spatial_extent",
                "ogr",
            )
            if vlayer:
                return True
        elif (
            all(i in self.result.keys() for i in ["type", "features"])
            and self.result.get("type").lower() == "featurecollection"
        ):
            # Process GeoJSON
            geojsons: [] = split_geojson_by_geometry(
                self.result,
                keep_geometry_less=self.dlg.check_keep_geometryless.isChecked(),
                combine_single_with_multi_geometries=self.dlg.check_merge_geometries.isChecked(),
            )
            for i in range(len(geojsons)):
                vlayer = create_ohsome_vector_layer(
                    self.iface,
                    geojsons[i],
                    self.request_time,
                    self.request_url,
                    self.activate_temporal,
                )
                postprocess_metadata(geojsons[i], vlayer)
            return True
        elif (
            "result" in self.result.keys()
            and len(self.result.get("result")) > 0
        ):
            # Process flat tables
            file = QgsProcessingUtils.generateTempFilename(
                f"{self.request_url}.csv"
            )
            header = self.result["result"][0].keys()
            vlayer = create_ohsome_csv_layer(
                self.iface,
                self.result["result"],
                header,
                file,
                self.request_time,
            )
            postprocess_metadata(self.result, vlayer)
            return True
        elif (
            "groupByResult" in self.result.keys()
            and len(self.result.get("groupByResult")) > 0
        ):
            # Process non-flat tables
            results = self.result["groupByResult"]
            for result_group in results:
                file = QgsProcessingUtils.generateTempFilename(
                    f'{result_group["groupByObject"]}_{self.request_url}.csv'
                )
                header = results[0]["result"][0].keys()
                vlayer = create_ohsome_csv_layer(
                    self.iface,
                    result_group["result"],
                    header,
                    file,
                    self.request_time,
                )
                postprocess_metadata(self.result, vlayer)
            return True
        elif (
            "ratioResult" in self.result.keys()
            and len(self.result.get("ratioResult")) > 0
        ):
            # Process flat tables
            file = QgsProcessingUtils.generateTempFilename(
                f"{self.request_url}.csv"
            )
            header = self.result.get("ratioResult")[0].keys()
            vlayer = create_ohsome_csv_layer(
                self.iface,
                self.result["ratioResult"],
                header,
                file,
                self.request_time,
            )
            postprocess_metadata(self.result, vlayer)
            return True
        return False

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        self.request_time = datetime.now().strftime("%m-%d-%Y:%H-%M-%S")
        logger.log(f'Started task "{self.description()}"', Qgis.Info)
        try:
            if len(self.preferences):
                self.result = self.client.request(
                    f"/{self.request_url}",
                    {},
                    post_json=self.preferences,
                )
            else:
                self.result = self.client.request(f"/metadata", {})
        except Exception as e:
            self.result = None
            self.exception = e
        return True

    def finished(self, valid_result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        You implement finished() to do whatever follow-up stuff
        should happen after the task is complete.
        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.
        result is the return value from self.run.
        """
        default_message = (
            f"\nAPI URL: {self.client.base_url}"
            f"\nEndpoint: {self.request_url}"
            f'\nPreferences: {json.dumps(self.preferences, indent=4, sort_keys=True)}"'
        )
        if "bpolys" in self.preferences:
            self.preferences[
                "bpolys"
            ] = "Geometry shortened. For issue/debug copy from 'View'->'Panels'->'Log Messages'."
        elif "bcircles" in self.preferences:
            self.preferences[
                "bcircles"
            ] = "Geometry shortened. For issue/debug copy from 'View'->'Panels'->'Log Messages'."
        shortened_default_message = (
            f"\nAPI URL: {self.client.base_url}"
            f"\nEndpoint: {self.request_url}"
            f'\nPreferences: {json.dumps(self.preferences, indent=4, sort_keys=True)}"'
        )
        if valid_result and self.result:
            msg = f"The request was successful:" + default_message
            short_msg = (
                f"The request was successful:" + shortened_default_message
            )
            try:
                if (
                    valid_result
                    and self.result
                    and "extractRegion" in self.result
                ):
                    default_message = (
                        f"\nAPI URL: {self.client.base_url}"
                        f"\nEndpoint: {self.request_url}"
                        f'\nMetadata Response: {json.dumps(self.result, indent=4, sort_keys=True)}"'
                    )
                    short_msg = msg = (
                        f"The request was successful:" + default_message
                    )
                    QMessageBox.information(
                        self.dlg,
                        "Ohsome Metadata",
                        "Metadata Response:\n"
                        f"attribution:\n{json.dumps(self.result.get('attribution'), indent=4, sort_keys=True)}\n"
                        f"apiVersion:{self.result.get('apiVersion')}\n"
                        f"spatialExtent: The spatial extent will be imported as a new layer.\n"
                        f"timeout:{self.result.get('timeout')}\n"
                        f"temporalExtent:\n{json.dumps(self.result.get('extractRegion').get('temporalExtent'), indent=4, sort_keys=True)}",
                    )

                self.postprocess_results()
                logger.log(msg, Qgis.Info)
                self.iface.messageBar().pushMessage(
                    "Info",
                    "Success!",
                    level=Qgis.Info,
                    duration=5,
                )
            except Exception as err:
                msg = (
                    f"> Error while processing the geometry response from Ohsome:"
                    + default_message
                    + f"\nException: {err}"
                )
                short_msg = (
                    f"> Error while processing the geometry response from Ohsome:"
                    + shortened_default_message
                    + f"\nException: {err}"
                )
                logger.log(msg, Qgis.Critical)
                self.iface.messageBar().pushMessage(
                    "Critical",
                    "Error while processing the returned geometries!",
                    level=Qgis.Critical,
                    duration=5,
                )
            finally:
                self.dlg.debug_text.append("> " + short_msg)
        elif self.client.canceled:
            msg = f"The request was canceled."
            logger.log(msg, Qgis.Warning)
            self.dlg.debug_text.append(msg)
            self.iface.messageBar().pushMessage(
                "Info",
                msg,
                level=Qgis.Info,
                duration=5,
            )
        elif self.exception:
            msg = (
                f"> The request was not successful and threw an exception:"
                + default_message
                + f"\nException: {self.exception}"
            )
            short_msg = (
                f"> The request was not successful and threw an exception:"
                + shortened_default_message
                + f"\nException: {self.exception}"
            )
            self.dlg.debug_text.append(short_msg)
            logger.log(msg, Qgis.Critical)
            self.iface.messageBar().pushMessage(
                "Warning",
                "The response is empty and an error was returned. "
                "Refine your filter query and check the log or plugin console for errors and exceptions.",
                level=Qgis.Critical,
                duration=5,
            )
            self.dlg.global_buttons.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            msg = (
                f"The request was not successful and the reason is unclear. This should not happen!"
                + default_message
                + f'\nResult: {json.dumps(self.result if self.result else {}, indent=4, sort_keys=True)}"'
                + f'\nException: {json.dumps(self.exception if self.exception else {}, indent=4, sort_keys=True)}"'
            )
            short_msg = (
                f"The request was not successful and the reason is unclear. This should not happen!"
                + shortened_default_message
                + f'\nResult: {json.dumps(self.result if self.result else {}, indent=4, sort_keys=True)}"'
                + f'\nException: {json.dumps(self.exception if self.exception else {}, indent=4, sort_keys=True)}"'
            )
            self.dlg.debug_text.append(short_msg)
            logger.log(msg, Qgis.Warning)
            self.iface.messageBar().pushMessage(
                "Warning",
                "The response is empty but without evident error. Refine your filter query and check the log or plugin console.",
                level=Qgis.Warning,
                duration=5,
            )
        self.dlg.global_buttons.button(QDialogButtonBox.Ok).setEnabled(True)

    def cancel(self):
        self.client.cancel()
        logger.log(
            "The Ohsome request was canceled by the user.",
            Qgis.Info,
        )
        super().cancel()
