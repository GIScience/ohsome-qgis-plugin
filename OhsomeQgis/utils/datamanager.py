import json

from PyQt5.QtWidgets import QListWidget
from qgis._core import QgsFeature, QgsGeometry, QgsWkbTypes, QgsPointXY


def check_list_duplicates(list_widget: QListWidget, item_name: str) -> bool:
    for i in range(list_widget.count()):
        if list_widget.item(i).text().__eq__(item_name):
            return True
    return False


from OhsomeQgis.utils import transform


def _get_layer_polygons(layer):
    """
    Extract polygon geometries from the selected polygon layer.

    :param layer: The polygon layer
    :type layer: QgsMapLayer
    :returns: GeoJSON object
    :rtype: dict
    """
    polygons = None
    transformer = transform.transformToWGS(layer.sourceCrs())
    features = layer.getFeatures()

    # iterate over all other features
    for feature in features:
        if feature.hasGeometry():
            geom = feature.geometry()
            geom.transform(transformer)
            if polygons is None:
                polygons = geom
            else:
                polygons = polygons.combine(geom)

    if not polygons:
        return json.loads("{}")
    else:
        return json.loads(polygons.asJson())


def convert_point_features_to_ohsome_bcircles(
    features: [QgsFeature], radii: [int]
):
    coordinates_list = []
    for i in range(len(features)):
        coordinates = None
        counter = 0
        for feature in features[i]:
            geometry: QgsGeometry = feature.geometry()
            if geometry.type() == QgsWkbTypes.PointGeometry:
                point: QgsPointXY = feature.geometry().asPoint()
                coordinates = (
                    f"{coordinates}|id{counter}:{point.x()},{point.y()},{radii[i]}"
                    if coordinates
                    else f"id{counter}:{point.x()},{point.y()},{radii[i]}"
                )
                counter += 1
        if coordinates:
            coordinates_list.append(coordinates)
    return coordinates_list
