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

import os.path
import configparser
from datetime import datetime


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load OSMtools class from file OS;tools.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    from .OhsomeQgisPlugin import OhsomeQgis

    return OhsomeQgis(iface)


# Define plugin wide constants
PLUGIN_NAME = "Ohsome Qgis"
DEFAULT_COLOR = "#a8b1f5"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_PREFIX = ":plugins/OhsomeQgis/img/"
CONFIG_PATH = os.path.join(BASE_DIR, "config.yml")

# Read metadata.txt
METADATA = configparser.ConfigParser()
METADATA.read(os.path.join(BASE_DIR, "metadata.txt"), encoding="utf-8")
today = datetime.today()

__version__ = METADATA["general"]["version"]
__author__ = METADATA["general"]["author"]
__email__ = METADATA["general"]["email"]
__web__ = METADATA["general"]["homepage"]
__help__ = METADATA["general"]["help"]
__date__ = today.strftime("%Y-%m-%d")
__copyright__ = "(C) {} by {}".format(today.year, __author__)
