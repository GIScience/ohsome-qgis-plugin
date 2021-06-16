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

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import QApplication

from qgis.gui import QgsMapToolEmitPoint

from OhsomeQgis import RESOURCE_PREFIX


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


# class PointTool(QgsMapToolEmitPoint):
#     """Point Map tool to capture mapped coordinates."""
#
#     def __init__(self, canvas, button):
#         """
#         :param canvas: current map canvas
#         :type: QgsMapCanvas
#
#         :param button: name of 'Map!' button pressed.
#         :type button: str
#         """
#
#         QgsMapToolEmitPoint.__init__(self, canvas)
#         self.canvas = canvas
#         self.button = button
#         self.cursor = QCursor(QPixmap(RESOURCE_PREFIX + 'icon_locate.png').scaledToWidth(48), 24, 24)
#
#     canvasClicked = pyqtSignal(['QgsPointXY', 'QString'])
#     def canvasReleaseEvent(self, event):
#         #Get the click and emit a transformed point
#
#         crsSrc = self.canvas.mapSettings().destinationCrs()
#
#         point_oldcrs = event.mapPoint()
#
#         xform = transform.transformToWGS(crsSrc)
#         point_newcrs = xform.transform(point_oldcrs)
#
#         QApplication.restoreOverrideCursor()
#
#         self.canvasClicked.emit(point_newcrs, self.button)
#
#     def activate(self):
#         QApplication.setOverrideCursor(self.cursor)
