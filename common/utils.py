#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ohsome utility functions """
"""
Original source: https://github.com/GIScience/ohsome-py

"""

import copy
from datetime import datetime

from PyQt5.QtCore import QDateTime, QVariant
from PyQt5.QtWidgets import QListWidget
from qgis.core import (
    QgsMapLayerType,
    QgsMapLayer,
    QgsVectorLayer,
    QgsFeatureIterator,
    QgsFeature,
    QgsGeometry,
    QgsWkbTypes,
    QgsPolygon,
    QgsMultiPolygon,
    QgsProject,
    Qgis,
    QgsField,
    QgsFields,
    QgsDataProvider,
    QgsVectorDataProvider,
    QgsPoint,
    QgsUnitTypes,
)
from qgis.utils import iface


def format_coordinates(feature_collection):
    """
    Format coordinates of feature to match ohsome requirements
    :param feature:
    :return:
    """
    features = feature_collection["features"]

    geometry_strings = []
    for feature in features:

        if feature["geometry"]["type"] == "Polygon":
            outer_ring = feature["geometry"]["coordinates"][0]
            geometry_strings.append(
                ",".join([str(c[0]) + "," + str(c[1]) for c in outer_ring])
            )
        elif feature["geometry"]["type"] == "MultiPolygon":
            outer_rings = feature["geometry"]["coordinates"][0]
            for ring in outer_rings:
                geometry_strings.append(
                    ",".join([str(c[0]) + "," + str(c[1]) for c in ring])
                )
        else:
            print("Geometry type is not implemented")

    return "|".join(geometry_strings)


def find_groupby_names(url):
    """
    Get the groupBy names
    :return:
    """
    return [name.strip("/") for name in url.split("groupBy")[1:]]


def format_geodataframe(geodataframe):
    """
    Converts a geodataframe to a json object to be passed to an ohsome request
    :param geodataframe:
    :return:
    """
    if not "id" in geodataframe.columns:
        UserWarning(
            "Dataframe does not contain an 'id' column. Joining the ohsome query results and the geodataframe will not be possible."
        )

    # Create a json object which holds geometry, id and osmid for ohsome query
    return geodataframe.loc[:, ["id", "geometry"]].to_json(na="drop")


def check_list_duplicates(list_widget: QListWidget, item_name: str) -> bool:
    for i in range(list_widget.count()):
        if list_widget.item(i).text().__eq__(item_name):
            return True
    return False


def combine_layer_geometries(qgsLayer: QgsMapLayer):
    geometries = list()
    if qgsLayer.type() == QgsMapLayerType.VectorLayer:
        geometries.extend(combine_features(qgsLayer.getFeatures()))
    return geometries


def combine_features(qgsFeatures: QgsFeatureIterator):
    geometries = list()
    feature: QgsPolygon
    for feature in qgsFeatures:
        if isinstance(feature, QgsPolygon):
            geometries.append(feature.asWkt(6))
        elif isinstance(feature, QgsMultiPolygon):
            print("test")
        elif isinstance(feature, QgsFeature):
            geometry: QgsGeometry = feature.geometry()
            if geometry.wkbType() == QgsWkbTypes.MultiPolygon:
                geometries.extend(combine_features(geometry.parts()))
    return geometries


def create_time_aware_qgsfeature(
    qgsFeature: QgsFeature, startDateTime: QDateTime, endDateTime: QDateTime
):
    pass


def load_layers_to_canvas(layer_list: list):
    vlayer: QgsVectorLayer
    for vlayer in layer_list:
        if not vlayer or not isinstance(vlayer, QgsVectorLayer) or not vlayer.isValid():
            iface.messageBar().pushMessage(
                "[Utils] Error", "A layer couldn't be added.", level=Qgis.Warning
            )
        else:
            QgsProject.instance().addMapLayer(vlayer)


def process_features(features: QgsFeatureIterator):
    processed_features = dict()
    unprocessed_feature: QgsFeature
    for unprocessed_feature in features:
        new_fields = QgsFields()
        new_attributes = list()
        start_date = None
        feature_id: str = None
        feature_type: str = None
        key: QgsField
        for field, attribute in zip(
            unprocessed_feature.fields(), unprocessed_feature.attributes()
        ):
            if isinstance(attribute, str) and (
                attribute.__contains__("node")
                or attribute.__contains__("way")
                or attribute.__contains__("relation")
            ):
                if attribute.__contains__("node"):
                    feature_type = "node"
                    feature_id = attribute.strip("node/")
                elif attribute.__contains__("way"):
                    feature_type = "way"
                    feature_id = attribute.strip("way/")
                elif attribute.__contains__("relation"):
                    feature_type = "relation"
                    feature_id = attribute.strip("relation/")
                if not feature_type in processed_features:
                    processed_features[feature_type] = dict()
            elif isinstance(attribute, QDateTime) and field.name().__contains__(
                "@snapshotTimestamp"
            ):
                start_date = attribute
            new_fields.append(field)
            new_attributes.append(attribute)
        new_fields.append(QgsField("startDate", QVariant.DateTime))
        new_attributes.append(start_date)
        new_fields.append(QgsField("endDate", QVariant.DateTime))
        new_attributes.append(QDateTime.currentDateTime())
        if new_fields.field("startDate") and new_fields.field("endDate"):
            unprocessed_feature.setFields(new_fields, initAttributes=True)
            unprocessed_feature.setAttributes(new_attributes)
            unprocessed_feature.setAttribute("endDate", QDateTime.currentDateTime())
            if processed_features[feature_type].keys().__contains__(feature_id):
                processed_features[feature_type][feature_id].append(unprocessed_feature)
                processed_features[feature_type][feature_id].sort(
                    key=lambda x: x.attribute("startDate")
                )
                last: QgsFeature = processed_features[feature_type][
                    feature_id
                ].__getitem__(len(processed_features[feature_type][feature_id]) - 1)
                processed_features[feature_type][feature_id].__getitem__(
                    len(processed_features[feature_type][feature_id]) - 2
                ).setAttribute("endDate", last.attribute("startDate").addSecs(-3600))
            else:
                processed_features[feature_type][feature_id] = list()
                processed_features[feature_type][feature_id].append(unprocessed_feature)
    return processed_features


def postprocess_vlayer(vlayer: QgsVectorLayer, activate_temporal: bool):
    pr = vlayer.dataProvider()

    # changes are only possible when editing the layer
    vlayer.startEditing()
    pr.addAttributes([QgsField("durationField", QVariant.Int)])  # Add durationsField
    vlayer.temporalProperties().setMode(1)  # Set the correct temporal mode
    vlayer.temporalProperties().setStartField("@snapshotTimestamp")
    vlayer.temporalProperties().setIsActive(activate_temporal)

    # commit to stop editing the layer
    vlayer.commitChanges()

    # update layer's extent when new features have been added
    # because change of extent in provider is not propagated to the layer
    vlayer.updateExtents()
    return vlayer


def combine_features_to_layer(
    processed_features: dict, old_vlayer: QgsVectorLayer, activate_temporal: bool = True
):
    processed_layers = list()
    data_provider = old_vlayer.dataProvider()
    # TODO Create the layers based on vector type not osmid
    feature_type: str
    for feature_type in processed_features:
        # create layer
        layer_type: str = ""
        if (
            data_provider.wkbType() == QgsWkbTypes.Point
            or data_provider.wkbType() == QgsWkbTypes.PointGeometry
        ):
            layer_type = "point"
        elif (
            data_provider.wkbType() == QgsWkbTypes.LineString
            or data_provider.wkbType() == QgsWkbTypes.LineGeometry
        ):
            layer_type = "linestring"
        elif (
            data_provider.wkbType() == QgsWkbTypes.Polygon
            or data_provider.wkbType() == QgsWkbTypes.PolygonGeometry
        ):
            layer_type = "polygon"
        elif data_provider.wkbType() == QgsWkbTypes.MultiPoint:
            layer_type = "multipoint"
        elif data_provider.wkbType() == QgsWkbTypes.MultiLineString:
            layer_type = "multilinestring"
        elif data_provider.wkbType() == QgsWkbTypes.MultiPolygon:
            layer_type = "multipolygon"
        else:
            continue
        vlayer = QgsVectorLayer(
            layer_type,
            f"{feature_type.capitalize()}_{layer_type.capitalize()}_OhsomeResult_{datetime.now()}",
            "memory",
        )
        pr: QgsVectorDataProvider = vlayer.dataProvider()
        # pr.addAttributes(old_vlayer.fields())
        # changes are only possible when editing the layer
        vlayer.startEditing()
        # add fields
        features = list()
        fields = QgsFields()
        # Add temporal fields
        for feature_collection in processed_features[feature_type]:
            [
                features.append(x)
                for x in processed_features[feature_type][feature_collection]
            ]
        if len(features) > 0:
            pr.addAttributes(features[0].fields())
        pr.addFeatures(features)
        vlayer.temporalProperties().setMode(2)  # Set the correct temporal mode
        vlayer.temporalProperties().setStartField("startDate")
        vlayer.temporalProperties().setEndField("endDate")
        vlayer.temporalProperties().setIsActive(activate_temporal)
        # commit to stop editing the layer
        vlayer.commitChanges()

        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        vlayer.updateExtents()
        processed_layers.append(vlayer)
    return processed_layers


def sort_and_combine_vector_layer(
    vlayer: QgsVectorLayer, activate_temporal: bool = True
) -> list:
    processed_features = process_features(vlayer.getFeatures())
    if len(processed_features) <= 0:
        iface.messageBar().pushMessage(
            "[Utils] Error", "Response empty.", level=Qgis.Warning
        )
        return list()
    return combine_features_to_layer(
        processed_features, vlayer, activate_temporal=activate_temporal
    )


def process_vector_layer(
    vlayer: QgsVectorLayer, activate_temporal: bool = True
) -> list:
    processed_features = process_features(vlayer.getFeatures())
    if len(processed_features) <= 0:
        iface.messageBar().pushMessage(
            "[Utils] Error", "Response empty.", level=Qgis.Warning
        )
        return list()

    return combine_features_to_layer(
        processed_features, vlayer.dataProvider(), activate_temporal=activate_temporal
    )


def get_layers():
    # Fetch the currently loaded layers
    layers: list = QgsProject.instance().mapLayers()

    # Populate the comboBox with names of all the loaded layers
    layer: QgsVectorLayer
    valid_layers: list = list()
    for layer_id, layer in layers.items():
        if layer.type() == QgsMapLayerType.VectorLayer and (
            layer.wkbType() == QgsWkbTypes.Polygon
            or layer.wkbType() == QgsWkbTypes.MultiPolygon
        ):
            valid_layers.append(layer)
    return valid_layers


def get_layer_by_name(name: str):
    if name:
        try:
            layer_filter: filter = filter(lambda x: x.name() == name, get_layers())
            return next(layer_filter)
        except Exception as err:
            iface.messageBar().pushMessage(
                f"[Utils] Couldn't find layer {name}", f"{err}", level=Qgis.Warning
            )
    return None


def convert_mixed_collection(feature_collection):
    sorted_collection = dict()
    if "features" not in feature_collection:
        return None
    for feature in feature_collection["features"]:
        try:
            feature_type = feature["geometry"]["type"]
            if feature_type not in sorted_collection.keys():
                sorted_collection[feature_type] = list()
            sorted_collection[feature_type].append(feature)
        except Exception as err:
            pass
    for collection in sorted_collection:
        feature_collection["features"] = sorted_collection[collection]
        sorted_collection[collection] = copy.deepcopy(feature_collection)
    return sorted_collection
