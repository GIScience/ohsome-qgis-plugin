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

from qgis.core import QgsMessageLog, Qgis

from OhsomeQgis import PLUGIN_NAME


def log(message, level_in=0):
    """
    Writes to QGIS inbuilt logger accessible through panel.

    :param message: logging message to write, error or URL.
    :type message: str

    :param level_in: integer representation of logging level.
    :type level_in: int
    """
    if level_in == 0:
        level = Qgis.Info
    elif level_in == 1:
        level = Qgis.Warning
    elif level_in == 2:
        level = Qgis.Critical
    else:
        level = Qgis.Info

    QgsMessageLog.logMessage(message, PLUGIN_NAME.strip(), level)