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

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import QApplication
from qgis.gui import QgsMapToolEmitPoint

from ohsomeTools import RESOURCE_PREFIX


class PointTool(QgsMapToolEmitPoint):
    """Line Map tool to capture mapped lines."""

    def __init__(self, canvas):
        """
        :param canvas: current map canvas
        :type canvas: QgsMapCanvas
        """
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.crsSrc = self.canvas.mapSettings().destinationCrs()
        self.points = []
        self.cursor = QCursor(
            QPixmap(RESOURCE_PREFIX + "icon_locate.png").scaledToWidth(48),
            24,
            24,
        )
        self.reset()

    def reset(self):
        """reset captured points."""

        self.points = []

    pointDrawn = pyqtSignal(["QgsPointXY", "int"])

    def canvasReleaseEvent(self, e):
        """Add marker to canvas and shows line."""
        new_point = self.toMapCoordinates(e.pos())
        self.points.append(new_point)

        self.pointDrawn.emit(new_point, self.points.index(new_point))

    doubleClicked = pyqtSignal()

    def canvasDoubleClickEvent(self, e):
        """Deletes markers from map canvas."""
        self.doubleClicked.emit()
        QApplication.restoreOverrideCursor()

    def activate(self):
        QApplication.setOverrideCursor(self.cursor)
