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
from PyQt5.QtWidgets import QTableView, QMessageBox
from qgis._core import (
    QgsVectorLayer,
    QgsFeatureIterator,
    QgsAttributeTableConfig,
    QgsVectorLayerCache,
    QgsVectorDataProvider,
)
from qgis._gui import (
    QgsAttributeTableFilterModel,
    QgsAttributeTableModel,
    QgsAttributeTableView,
)

from qgis.core import (
    QgsPoint,
    QgsPointXY,
    QgsGeometry,
    QgsFeature,
    QgsFields,
    QgsField,
)

from OhsomeQgis.gui.ohsome_gui import OhsomeSpec
from OhsomeQgis.utils import convert


def get_request_point_features(route_dict, row_by_row):
    """
    Processes input point features depending on the layer to layer relation in directions settings

    :param route_dict: all coordinates and ID field values of start and end point layers
    :type route_dict: dict

    :param row_by_row: Specifies whether row-by-row relation or all-by-all has been used.
    :type row_by_row: str

    :returns: tuple of coordinates and ID field value for each routing feature in route_dict
    :rtype: tuple
    """

    locations_list = list(
        product(
            route_dict["start"]["geometries"], route_dict["end"]["geometries"]
        )
    )
    values_list = list(
        product(route_dict["start"]["values"], route_dict["end"]["values"])
    )

    # If row-by-row in two-layer mode, then only zip the locations
    if row_by_row == "Row-by-Row":
        locations_list = list(
            zip(
                route_dict["start"]["geometries"],
                route_dict["end"]["geometries"],
            )
        )

        values_list = list(
            zip(route_dict["start"]["values"], route_dict["end"]["values"])
        )

    for properties in zip(locations_list, values_list):
        # Skip if first and last location are the same
        if properties[0][0] == properties[0][-1]:
            continue

        coordinates = [[round(x, 6), round(y, 6)] for x, y in properties[0]]
        values = properties[1]

        yield (coordinates, values)


def get_fields(
    from_type=QVariant.String,
    to_type=QVariant.String,
    from_name="FROM_ID",
    to_name="TO_ID",
    line=False,
):
    """
    Builds output fields for directions response layer.

    :param from_type: field type for 'FROM_ID' field
    :type from_type: QVariant enum

    :param to_type: field type for 'TO_ID' field
    :type to_type: QVariant enum

    :param from_name: field name for 'FROM_ID' field
    :type from_name: str

    :param to_name: field name for 'TO_ID' field
    :type to_name: field name for 'TO_ID' field

    :param line: Specifies whether the output feature is a line or a point
    :type line: boolean

    :returns: fields object to set attributes of output layer
    :rtype: QgsFields
    """

    fields = QgsFields()
    fields.append(QgsField("DIST_KM", QVariant.Double))
    fields.append(QgsField("DURATION_H", QVariant.Double))
    fields.append(QgsField("PROFILE", QVariant.String))
    fields.append(QgsField("PREF", QVariant.String))
    fields.append(QgsField("OPTIONS", QVariant.String))
    fields.append(QgsField(from_name, from_type))
    if not line:
        fields.append(QgsField(to_name, to_type))

    return fields


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
    if len(vlayer) <= 0:
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


def get_output_feature_extraction(response: dict, preference: OhsomeSpec):
    """
    Build output feature based on response attributes for the data extraction endpoint.

    :param response: API response object
    :type response: dict

    :param preference: API request preferences being used.
    :type preference: dict

    :returns: Output feature with attributes and geometry set.
    :rtype: QgsFeature
    """
    response_mini = response["features"][0]
    feat = QgsFeature()
    coordinates = response_mini["geometry"]["coordinates"]
    distance = response_mini["properties"]["summary"]["distance"]
    duration = response_mini["properties"]["summary"]["duration"]
    qgis_coords = [QgsPoint(x, y, z) for x, y, z in coordinates]
    feat.setGeometry(QgsGeometry.fromPolyline(qgis_coords))
    feat.setAttributes(
        [
            "{0:.3f}".format(distance / 1000),
            "{0:.3f}".format(duration / 3600),
            profile,
            preference,
            str(options),
            from_value,
            to_value,
        ]
    )

    return feat


def get_output_features_optimization(response, profile, from_value=None):
    """
    Build output feature based on response attributes for optimization endpoint.

    :param response: API response object
    :type response: dict

    :param profile: transportation profile to be used
    :type profile: str

    :param from_value: value of 'FROM_ID' field
    :type from_value: any

    :returns: built feature
    :rtype: QgsFeature
    """

    response_mini = response["routes"][0]
    feat = QgsFeature()
    polyline = response_mini["geometry"]
    distance = response_mini["distance"]
    duration = response_mini["cost"]
    qgis_coords = [
        QgsPointXY(x, y) for x, y in convert.decode_polyline(polyline)
    ]
    feat.setGeometry(QgsGeometry.fromPolylineXY(qgis_coords))
    feat.setAttributes(
        [
            "{0:.3f}".format(distance / 1000),
            "{0:.3f}".format(duration / 3600),
            profile,
            "fastest",
            "optimized",
            from_value,
        ]
    )

    return feat
