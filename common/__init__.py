# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OhsomeTools
                                 A QGIS plugin
 QGIS client to query ohsome
                              -------------------
        begin                : 2020-06-22
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Julian Psotta
        email                : julianpsotta@gmail.com
 ***************************************************************************/

 This plugin provides access to the various APIs from Ohsome
 (https://ohsome.org).
 The original code for the modules inside the common folder can be found at:
 https://github.com/GIScience/ohsome-py

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

PROFILES = [
    'data_extraction'
]

DIMENSIONS = ['bbox', 'centroid', 'geometry']

PREFERENCES = ['fastest', 'shortest']
