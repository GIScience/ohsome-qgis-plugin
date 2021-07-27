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

import os.path
import configparser
from datetime import datetime


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load OSMtools class from file OS;tools.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    from .OhsomeToolsPlugin import OhsomeTools

    globals()["global_date_status_message"] = "Empty"

    return OhsomeTools(iface)


# Define plugin wide constants
PLUGIN_NAME = "ohsomeTools"
DEFAULT_COLOR = "#a8b1f5"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_PREFIX = ":plugins/ohsomeTools/img/"
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
__filter_help__ = METADATA["general"]["filter_help"]
__date__ = today.strftime("%Y-%m-%d")
__copyright__ = "(C) {} by {}".format(today.year, __author__)
