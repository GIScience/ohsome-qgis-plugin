# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OhsomeQgis
                                 A QGIS plugin
 QGIS client to query the ohsome api
                              -------------------
        begin                : 2021-05-01
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Julian Psotta
        email                : julianpsotta@gmail.com
 ***************************************************************************/

 This plugin provides access to the API from Ohsome
 (https://ohsome.org), developed and
 maintained by GIScience team at University of Heidelberg, Germany.
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
import random
from datetime import datetime
from itertools import product
from time import sleep

from PyQt5.QtCore import QVariant, Qt, QUrl
from PyQt5.QtWidgets import QDialogButtonBox
from qgis._core import (
    QgsVectorLayer,
    QgsVectorDataProvider,
    QgsTask,
    QgsMessageLog,
    Qgis,
    QgsNetworkContentFetcherTask,
    QgsProcessingUtils,
)

from qgis.core import (
    QgsFeature,
    QgsField,
)

from OhsomeQgis.common import client
from OhsomeQgis.gui.ohsome_gui import OhsomeSpec
from OhsomeQgis.utils import exceptions, logger


def write_ohsome_vector_layer(
    iface, file: str, request_time: str
) -> QgsVectorLayer:
    return iface.addVectorLayer(
        file,
        f"ohsome_" f"{request_time}",
        "ogr",
    )


def split_geojson_by_geometry(geojson: dict) -> [dict]:
    geojson_per_geometry = []
    features_per_geometry = {}
    features = geojson.pop("features")
    for feature in features:
        try:
            geometry_type = feature["geometry"]["type"]
            if geometry_type not in features_per_geometry:
                features_per_geometry[geometry_type] = []
            features_per_geometry[geometry_type].append(feature)
        except Exception as err:
            print("")
    for _, feature_set in features_per_geometry.items():
        temp_geojson = geojson.copy()
        temp_geojson["features"] = feature_set
        geojson_per_geometry.append(temp_geojson)
        del temp_geojson
    return geojson_per_geometry


def postprocess_qgsvectorlayer(vlayer: QgsVectorLayer, activate_temporal: bool):
    if not vlayer or len(vlayer) <= 0:
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
    features = sorted(features, key=lambda sort_id: sort_id["@osmId"])
    vlayer.dataProvider().deleteFeatures([feature.id() for feature in features])
    for i in range(len(features)):
        feature: QgsFeature = features[i]
        if (
            i < len(features) - 1
            and features[i + 1]["@osmId"] == feature["@osmId"]
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
        preferences: dict,
        activate_temporal: bool = False,
    ):
        super().__init__(description, QgsTask.CanCancel)
        self.iface = iface
        self.dlg = dlg
        self.total = 0
        self.iterations = 0
        self.exception = None
        self.request_url = request_url
        self.preferences = preferences
        self.activate_temporal = activate_temporal
        self.result: dict = {}
        self.request_time = None
        self.client = client.Client(provider)

    def postprocess_results(self) -> bool:
        if not self.result or not len(self.result):
            return False

        if (
            all(i in self.result.keys() for i in ["type", "features"])
            and self.result.get("type").lower() == "featurecollection"
        ):
            # Process GeoJSON
            geojsons: [] = split_geojson_by_geometry(self.result)
            for i in range(len(geojsons)):
                file = QgsProcessingUtils.generateTempFilename(
                    f"{self.request_url}.geojson"
                )
                with open(file, "w") as f:
                    f.write(json.dumps(geojsons[i], indent=4))
                vlayer = write_ohsome_vector_layer(
                    self.iface, file, self.request_time
                )
                postprocess_qgsvectorlayer(
                    vlayer,
                    activate_temporal=self.activate_temporal,
                )
            return True
        elif (
            "result" in self.result.keys()
            and len(self.result.get("result")) > 0
        ):
            # Process flat tables
            file = QgsProcessingUtils.generateTempFilename(
                f"{self.request_url}.csv"
            )
            results = self.result["result"]
            with open(file, "w", newline="") as f:
                wr = csv.DictWriter(
                    f,
                    fieldnames=results[0].keys(),
                )
                wr.writeheader()
                for row_result in results:
                    wr.writerow(row_result)
            vlayer = write_ohsome_vector_layer(
                self.iface, file, self.request_time
            )
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
                with open(file, "w", newline="") as f:
                    wr = csv.DictWriter(
                        f,
                        fieldnames=results[0]["result"][0].keys(),
                    )
                    wr.writeheader()
                    for row_result in result_group["result"]:
                        wr.writerow(row_result)
                vlayer = write_ohsome_vector_layer(
                    self.iface, file, self.request_time
                )
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

            self.result = self.client.request(
                f"/{self.request_url}",
                {},
                post_json=self.preferences,
            )
        except Exception as e:
            raise e
        logger.log(f'Task direct response "{self.result}"', Qgis.Info)

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
            f'API URL: {self.client.base_url}\n"'
            f'Endpoint: {self.request_url}\n"'
            f'Preferences: {json.dumps(self.preferences, indent=4, sort_keys=True)}"'
        )
        if valid_result and self.result:
            msg = f"The request was successful:\n" + default_message
            logger.log(msg, Qgis.Warning)
            self.iface.messageBar().pushMessage(
                "Info",
                "Success!",
                level=Qgis.Info,
                duration=5,
            )
            self.dlg.debug_text.append(">" + msg)
            self.postprocess_results()

        elif self.client.canceled:
            msg = f'Task "{self.description()}" canceled.'
            logger.log(msg, Qgis.Warning)
            self.dlg.debug_text.setText(msg)
            self.iface.messageBar().pushMessage(
                "Info",
                msg,
                level=Qgis.Info,
                duration=5,
            )
        elif self.exception:
            msg = (
                f"The request was not successful and threw an exception:\n"
                + default_message
                + f"\nException: {self.exception}"
            )
            self.dlg.debug_text.setText(msg)
            logger.log(msg, Qgis.Critical)
            self.iface.messageBar().pushMessage(
                "Warning",
                "The response is empty and an error was returned. Refine your filter query and check the plugin console for errors.",
                level=Qgis.Critical,
                duration=5,
            )
            raise self.exception
        else:
            msg = (
                f"The request was not successful and the reason is unclear. This should not happen!\n"
                + default_message
                + f'\nPreferences: {json.dumps(self.preferences, indent=4, sort_keys=True)}"'
            )
            self.dlg.debug_text.setText(msg)
            logger.log(msg, Qgis.Warning)
            self.iface.messageBar().pushMessage(
                "Warning",
                "The response is empty but without evident error. Refine your filter query and check the plugin console.",
                level=Qgis.Warning,
                duration=5,
            )
        self.dlg.global_buttons.button(QDialogButtonBox.Ok).setEnabled(True)

    def cancel(self):
        self.client.cancel()
        logger.log(
            'RandomTask "{name}" was canceled'.format(name=self.description()),
            Qgis.Info,
        )
        super().cancel()
