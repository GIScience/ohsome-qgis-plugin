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
import os

import yaml

from ohsomeTools import CONFIG_PATH


def read_config():
    """
    Reads config.yml from file and returns the parsed dict.

    :returns: Parsed settings dictionary.
    :rtype: dict
    """
    with open(CONFIG_PATH) as f:
        doc = yaml.safe_load(f)

    return doc


def write_config(new_config):
    """
    Dumps new config

    :param new_config: new provider settings after altering in dialog.
    :type new_config: dict
    """
    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(new_config, f)


def write_env_var(key, value):
    """
    Update quota env variables

    :param key: environment variable to update.
    :type key: str

    :param value: value for env variable.
    :type value: str
    """
    os.environ[key] = value
