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

import json
import re

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QCheckBox, QMessageBox, QDialog

from OhsomeQgis.common import GLOBAL_TIMEOUT
from OhsomeQgis.utils import transform


def _get_avoid_polygons(layer):
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


def _get_avoid_options(avoid_boxes):
    """
    Extracts checked boxes in Advanced avoid parameters.

    :param avoid_boxes: all checkboxes in advanced paramter dialog.
    :type avoid_boxes: list of QCheckBox

    :returns: avoid_features parameter
    :rtype: JSON dump, i.e. str
    """
    avoid_features = []
    for box in avoid_boxes:
        if box.isChecked():
            avoid_features.append((box.text()))

    return avoid_features


class Spec:
    """Extended functionality for all endpoints for the GUI."""

    def __init__(self, dlg: QDialog):
        """
        :param dlg: Main GUI dialog.
        :type dlg: QDialog
        """
        self.dlg: QDialog = dlg

    @property
    def _api_spec(self):
        return self.dlg.ohsome_spec_selection_combo.currentText()

    @property
    def _activate_temporal_feature(self):
        if self.dlg.check_activate_temporal.isChecked():
            return True
        return False

    @property
    def _show_metadata(self) -> bool:
        # Get all parameters
        if self.dlg.check_show_metadata.isChecked():
            return True
        return False

    @property
    def _request_timeout(self) -> int:
        if self.dlg.timeout_input.value():
            return int(self.dlg.timeout_input.value())
        return GLOBAL_TIMEOUT

    @property
    def _data_extraction_clip_geometry(self) -> bool:
        if self.dlg.check_clip_geometry.isChecked():
            return True
        return False

    @property
    def _property_groups(self) -> str:
        properties = ""
        if self.dlg.property_groups_check_tags.isChecked():
            properties = "tags"
        if self.dlg.property_groups_check_metadata.isChecked():
            properties = f"{properties},metadata"
        return properties

    @property
    def _data_aggregation_format(self) -> str:
        return self.dlg.data_aggregation_format.currentText()

    @property
    def _request_bcircles_coordinates(self) -> str:
        coordinate_string = ""
        layers_list = self.dlg.ohsome_centroid_location_list
        for idx in range(layers_list.count()):
            item: str = layers_list.item(idx).text()
            param_cords, radius = item.rsplit(" | Radius: ")
            _, coordinates = param_cords.split(": ")

            if len(coordinate_string) <= 0:
                coordinate_string = f"id{idx}:{coordinates},{radius}"
            else:
                coordinate_string = (
                    f"{coordinate_string}|id{idx}:{coordinates},{radius}"
                )
        return coordinate_string

    @property
    def _request_filter(self) -> str:
        if len(self.dlg.filter_input.toPlainText()) <= 0:
            QMessageBox.critical(
                self.dlg, "Filter error", "Set a filter query."
            )
            return ""
        return self.dlg.filter_input.toPlainText()

    @property
    def _request_url(self):
        # Construct request url
        request_url = (
            f"/{self.dlg.ohsome_spec_preference_combo.currentText()}/"
            f"{self.dlg.ohsome_spec_preference_specification.currentText()}"
        )
        return request_url

    @property
    def _request_date_string(self) -> str:
        date_string = self.__prepare_ohsome_time_parameter(
            self.dlg.date_start.date(),
            self.dlg.date_end.date(),
            self.dlg.interval_years.value(),
            self.dlg.interval_months.value(),
            self.dlg.interval_days.value(),
        )
        return date_string

    @property
    def is_valid(self) -> bool:
        if (
            len(self._request_bcircles_coordinates) <= 0
        ):  # TODO Add another check for the layer coordinates!
            return False
        if len(self._request_filter) <= 0:
            return False
        if len(self._request_url) <= 3:
            return False
        if len(self._request_date_string) <= 0:
            return False
        return True

    def __prepare_ohsome_time_parameter(
        self,
        start_date: QDate,
        end_date: QDate,
        years: int,
        months: int,
        days: int,
    ) -> str:
        """
        Prepare a valid ohsome time string to include into the API query.

        @return Returns a valid date parameter or raises a QGIS Warning and returns an empty string.
        @rtype: str
        """
        date_start = start_date.toString("yyyy-MM-dd")
        date_end = end_date.toString("yyyy-MM-dd")
        intervals = "/P"

        if years and years > 0:
            intervals = f"{intervals}{years}Y"
        if months and months > 0:
            intervals = f"{intervals}{months}M"
        if days and days > 0:
            intervals = f"{intervals}{days}D"

        # If it's the default date the API will reject all requests that are not equal or greater than the first second.
        if date_start == "2007-10-08":
            date_start = "2007-10-08T00:00:01"
        if date_end == "2007-10-08":
            date_end = "2007-10-08T00:00:01"

        # Check if intervals is misconstructed.
        if self._api_spec.lower() == "data-aggregation" and len(intervals) >= 3:
            dates = f"{date_start}/{date_end}{intervals}"
        else:
            dates = f"{date_start},{date_end}"
        return dates

    def __prepare_request_properties(self):
        """
        Builds parameters across different api specification combinations. Not all api endpoints support the same set of parameters.

        @return: All parameter mappings according the endpoint restrictions.
        @rtype: dict
        """
        properties = {}
        if self._api_spec.lower() == "data-extraction":
            properties[
                "clipGeometry"
            ] = self._data_extraction_clip_geometry.__str__().lower()
            if len(self._property_groups) > 0:
                properties["properties"] = self._property_groups
        elif self._api_spec.lower() == "data-aggregation":
            properties["format"] = self._data_aggregation_format
        properties["showMetadata"] = self._show_metadata.__str__().lower()
        properties["filter"] = self._request_filter
        properties["time"] = self._request_date_string
        properties["timeout"] = self._request_timeout

        return properties

    def get_bcircles_request_preferences(self):
        endpoint_specific_request_properties = (
            self.__prepare_request_properties()
        )
        endpoint_specific_request_properties[
            "bcircles"
        ] = self._request_bcircles_coordinates
        return endpoint_specific_request_properties

    def get_request_url(self) -> str:
        return self._request_url
