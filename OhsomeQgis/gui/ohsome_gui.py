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

from OhsomeQgis.gui import OhsomeQgisDialog
from OhsomeQgis.utils import transform, logger


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
        self.preferences_valid = False

        self.dlg: QDialog = dlg

        self._request_preferences = self._prepare_request_preferences()
        self._centroid_features = self.__prepare_centroid_features()
        if (
            len(self._request_preferences) > 0
            and len(self._centroid_features) > 0
        ):
            self.preferences_valid = True

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
        intervals = "P"

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

        # Check if intervals only contains P or less. Than it is invalid.
        if len(intervals) <= 1:
            QMessageBox.critical(
                self.dlg,
                "Interval error",
                "Set at least years, months or days for a valid interval.",
            )
            return ""
        elif date_start.__eq__(date_end):
            QMessageBox.critical(
                self.dlg, "Date error", "Start and end date must be different."
            )
            return ""

        dates = f"{date_start}/{date_end}/{intervals}"
        return dates

    def _prepare_request_preferences(self) -> dict:
        """
        Builds parameters across directions functionalities.

        @return: All parameter mappings except for coordinates or layers.
        @rtype: dict
        """
        preferences = {
            "activate_temporal_feature": False,
            "api_spec": self.dlg.ohsome_spec_selection_combo.currentText(),
            "api_preference": self.dlg.ohsome_spec_preference_combo.currentText(),
        }

        if self.dlg.check_activate_temporal.isChecked():
            preferences["activate_temporal_feature"] = True

        parameters = {"showMetadata": "false"}

        # Get options
        if self.dlg.check_show_metadata.isChecked():
            parameters["showMetadata"] = "true"

        # Check if a filter is set
        if len(self.dlg.filter_input.toPlainText()) <= 0:
            QMessageBox.critical(
                self.dlg, "Filter error", "Set a filter query."
            )
            return {}
        else:
            parameters["filter"] = self.dlg.filter_input.toPlainText()

        parameters["date_string"] = self.__prepare_ohsome_time_parameter(
            self.dlg.date_start.date(),
            self.dlg.date_end.date(),
            self.dlg.interval_years.value(),
            self.dlg.interval_months.value(),
            self.dlg.interval_days.value(),
        )
        # Check if the date string is valid. Else return an empty array.
        if len(parameters["date_string"]) <= 0:
            return {}
        preferences["parameters"] = parameters
        return preferences

    def __prepare_centroid_features(self) -> list:
        coordinate_string = ""
        layers_list = self.dlg.ohsome_centroid_location_list
        for idx in range(layers_list.count()):
            item: str = layers_list.item(idx).text()
            param_cords, radius = item.rsplit(" | Radius: ")
            _, coordinates = param_cords.split(": ")

            if len(coordinate_string) <= 0:
                coordinate_string = [f"id{idx}:{coordinates},{radius}"]
            else:
                coordinate_string = [
                    f"{coordinate_string}|id{idx}:{coordinates},{radius}"
                ]

        return coordinate_string

    def get_bcircles_request_preferences(self):
        return self._centroid_features
