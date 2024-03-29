# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ohsomeTools
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

from PyQt5.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from ohsomeTools.proc.data_aggregation import (
    elements_aggregation,
    elements_ratio_aggregation,
    contributions_count,
    users_count,
)
from ohsomeTools.proc.data_extraction import elements, contributions

from ohsomeTools import RESOURCE_PREFIX, PLUGIN_NAME, __version__


class OhsomeToolsProvider(QgsProcessingProvider):
    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        # data-aggregation
        self.addAlgorithm(elements_aggregation.ElementsAggregation())
        self.addAlgorithm(elements_ratio_aggregation.ElementsRatioAggregation())
        self.addAlgorithm(contributions_count.ContributionsCount())
        self.addAlgorithm(users_count.UsersCount())

        # data-extraction
        self.addAlgorithm(contributions.Contributions())
        self.addAlgorithm(elements.Elements())

    def icon(self):
        return QIcon(RESOURCE_PREFIX + "icon_ohsome.png")

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return PLUGIN_NAME.strip()

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return PLUGIN_NAME

    def longName(self):
        """
        Returns the longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return PLUGIN_NAME + " plugin v" + __version__
