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

from itertools import product
from PyQt5.QtCore import QVariant, Qt
from qgis._core import (
    QgsVectorLayer,
    QgsVectorDataProvider,
)

from qgis.core import (
    QgsFeature,
    QgsField,
)

from OhsomeQgis.gui.ohsome_gui import OhsomeSpec


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
