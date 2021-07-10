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

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
)


def transformToWGS(old_crs):
    """
    Returns a transformer to WGS84

    :param old_crs: CRS to transfrom from
    :type old_crs: QgsCoordinateReferenceSystem

    :returns: transformer to use in various modules.
    :rtype: QgsCoordinateTransform
    """
    outCrs = QgsCoordinateReferenceSystem(4326)
    xformer = QgsCoordinateTransform(old_crs, outCrs, QgsProject.instance())

    return xformer
