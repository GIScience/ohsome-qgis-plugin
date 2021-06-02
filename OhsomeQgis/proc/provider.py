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

from PyQt5.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from OhsomeQgis import RESOURCE_PREFIX, PLUGIN_NAME, __version__
from .isochrones_layer_proc import ORSisochronesLayerAlgo
from .isochrones_point_proc import ORSisochronesPointAlgo
from .matrix_proc import ORSmatrixAlgo
from .directions_points_layers_proc import ORSdirectionsPointsLayersAlgo
from .directions_points_layer_proc import ORSdirectionsPointsLayerAlgo
from .directions_lines_proc import ORSdirectionsLinesAlgo


class OhsomeQgisProvider(QgsProcessingProvider):
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
        #
        self.addAlgorithm(ORSdirectionsPointsLayersAlgo())
        self.addAlgorithm(ORSdirectionsPointsLayerAlgo())
        self.addAlgorithm(ORSdirectionsLinesAlgo())
        self.addAlgorithm(ORSisochronesLayerAlgo())
        self.addAlgorithm(ORSisochronesPointAlgo())
        self.addAlgorithm(ORSmatrixAlgo())

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
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return PLUGIN_NAME + " plugin v" + __version__