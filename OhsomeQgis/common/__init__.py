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

API_ENDPOINTS = [
    "Data-Extraction",
    "Data-Aggregation",
]

DIMENSIONS = ["time", "distance"]

PREFERENCES = ["fastest", "shortest", "recommended"]
GLOBAL_TIMEOUT = 10
EXTRACTION_SPECS = {
    "contributions": [
        "bbox",
        "centroid",
        "geometry",
        "latest/bbox",
        "latest/centroid",
        "latest/geometry",
    ],
    "elements": ["bbox", "centroid", "geometry"],
    "elementsFullHistory": ["bbox", "centroid", "geometry"],
}
AGGREGATION_SPECS = {
    "contributions/count": ["count/density"],
    "elements/area": [
        "density",
        "density/groupBy/boundary",
        # "density/groupBy/boundary/groupBy/tag",
        # "density/groupBy/tag",
        "density/groupBy/type",
        "groupBy/boundary",
        # "groupBy/boundary/groupBy/tag",
        # "groupBy/key",
        # "groupBy/tag",
        "groupBy/type",
        # "ratio",
        # "ratio/groupBy/boundary",
    ],
    "elements/count": [
        "density",
        "density/groupBy/boundary",
        # "density/groupBy/boundary/groupBy/tag",
        # "density/groupBy/tag",
        "density/groupBy/type",
        "groupBy/boundary",
        # "groupBy/boundary/groupBy/tag",
        # "groupBy/key",
        # "groupBy/tag",
        "groupBy/type",
        # "ratio",
        # "ratio/groupBy/boundary",
    ],
    "elements/length": [
        "density",
        "density/groupBy/boundary",
        # "density/groupBy/boundary/groupBy/tag",
        # "density/groupBy/tag",
        "density/groupBy/type",
        "groupBy/boundary",
        # "groupBy/boundary/groupBy/tag",
        # "groupBy/key",
        # "groupBy/tag",
        "groupBy/type",
        # "ratio",
        # "ratio/groupBy/boundary",
    ],
    "elements/perimeter": [
        "density",
        "density/groupBy/boundary",
        # "density/groupBy/boundary/groupBy/tag",
        # "density/groupBy/tag",
        "density/groupBy/type",
        "groupBy/boundary",
        # "groupBy/boundary/groupBy/tag",
        # "groupBy/key",
        # "groupBy/tag",
        "groupBy/type",
        # "ratio",
        # "ratio/groupBy/boundary",
    ],
    "users/count": [
        "density",
        "density/groupBy/boundary",
        # "density/groupBy/tag",
        "density/groupBy/type",
        "groupBy/boundary",
        # "groupBy/key",
        # "groupBy/tag",
        "groupBy/type",
    ],
}
DATA_AGGREGATION_FORMAT = {
    "groupBy/boundary": [
        "geojson",
        "json",
        "csv",
    ],
    "default": [
        "json",
        "csv",
    ],
}
