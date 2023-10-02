# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingParameterNumber,
    QgsProcessingAlgorithm,
    QgsProcessingParameterEnum,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDateTime,
    QgsWkbTypes,
    QgsProcessing,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFileDestination,
)

from qgis.utils import iface

from ohsomeTools.utils import configmanager

from ohsomeTools.common import AGGREGATION_SPECS, client
from ohsomeTools.proc.procDialog import run_processing_alg


class ElementsRatioAggregation(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    LAYER = "LAYER"
    PARAMETER = "PARAMETER"
    INPUT = "INPUT"
    FILTER = "FILTER"
    FILTER_2 = "FILTER_2"
    check_activate_temporal = "check_activate_temporal"
    check_show_metadata = "check_show_metadata"
    timeout_input = "timeout_input"
    check_clip_geometry = "check_clip_geometry"
    property_groups_check_tags = "property_groups_check_tags"
    property_groups_check_metadata = "property_groups_check_metadata"
    data_aggregation_format = "data_aggregation_format"
    date_start = "date_start"
    date_end = "date_end"
    YEARS = "YEARS"
    MONTHS = "MONTHS"
    DAYS = "DAYS"
    RADIUS = "RADIUS"
    GROUPBY = "GROUPBY"
    check_keep_geometryless = "check_keep_geometryless"
    check_merge_geometries = "check_merge_geometries"
    group_by_values_line_edit = "group_by_values_line_edit"
    group_by_key_line_edit = "group_by_key_line_edit"
    formats = ["json", "geojson"]
    parameters = [
        i.split("/")[1] for i in AGGREGATION_SPECS.keys() if "elements" in i
    ]
    PERIOD = "PERIOD"
    group_by_boundary = "group_by_boundary"
    PROVIDER = "PROVIDER"
    OUTPUT = "OUTPUT"

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return ElementsRatioAggregation()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return "elementsratioaggregation"

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("Elements Ratio Aggregation")

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr("Data Aggregation")

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return "dataaggregation"

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it.
        """
        return self.tr(
            """
        <p>Elements Ratio endpoints for the <strong>Ohsome-API</strong>. See <a href="https://docs.ohsome.org/ohsome-api/v1/">documentation</a>. </p>
        <p><strong>Parameters</strong></p>
        <ul>
        <li><em>Input</em>: Polygons will be passed "as is" (bpoly), points will be passed with radius (bcircles).</li>
        <li><em>Start-/ End-Date and Time</em>: Time in UTC.</li>
        <li><em>Point Layer Radius</em>: Radius for point layers.</li>
        <li><em>Period</em>: ISO 8601 Period, eg. /P1M for a monthly aggregation.</li>
        <li><em>Show Metadata</em>: Include metadata into the query response. Depending on the request of the request this can increase the response data size significantly.</li>
        <li><em>Keep without geometry</em>: Some results don&#39;t contain geometries but metadata. Decide if you wan&#39;t to keep them or only return ones with geometries. If checked, the geometry less features will be stored separately.</li>
        <li><em>Harmonize geometries</em>: Check this to <ins>automatically merge compatible geometry types</ins> It is recommended to keep this checked. The benefit is that the amount of written layers will be massively reduced. The reason is that results may contain single and multi-geometries at once (Polygon, MultiPolygon etc.) and without combining them one layer per geometry type will be written, resulting in an increased number of layers.</li>
        <li><em>Qgis temporal feature</em>: Automatically enable the temporal feature for new layers where applicable. This is only applied to responses that contain geometries and in that manner only on those geometry layers it makes sense for.</li>
        <li><em>Clip geometries</em>: Specify whether the returned geometries of the features should be clipped to the query’s spatial boundary. <ins>Ony available for the data extraction endpoints</ins></li>
        </ul>
        """
        )

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        # get dates from metadata
        try:
            provider = configmanager.read_config()["providers"][0]
            clnt = client.Client(provider)
            metadata = clnt.check_api_metadata(iface)

            start_date_string = (
                metadata.get("extractRegion")
                .get("temporalExtent")
                .get("fromTimestamp")
            )

            end_date_string = (
                metadata.get("extractRegion")
                .get("temporalExtent")
                .get("toTimestamp")
            )
        except:
            start_date_string = ""
            end_date_string = ""

        # We add the input vector features source. It can have any kind of
        # geometry.

        self.addParameter(
            QgsProcessingParameterEnum(
                self.PROVIDER,
                self.tr("Provider"),
                options=[
                    i["name"] for i in configmanager.read_config()["providers"]
                ],
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.LAYER,
                self.tr("Input"),
                [
                    QgsProcessing.TypeVectorPolygon,
                    QgsProcessing.TypeVectorPoint,
                ],
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr("Output"),
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.RADIUS,
                "Radius [m]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1000,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.PARAMETER,
                self.tr("Aggregation Type"),
                options=self.parameters,
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.group_by_boundary,
                self.tr("Group by Boundary"),
                defaultValue=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.group_by_values_line_edit,
                self.tr("Group by Values"),
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.group_by_key_line_edit,
                self.tr("Group by Key"),
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                self.date_start, "Start Date", defaultValue=start_date_string
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                self.date_end, "End Date", defaultValue=end_date_string
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PERIOD, "Period (ISO 8601)", defaultValue="/P1M"
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.FILTER,
                self.tr("Filter"),
                defaultValue="building=* or (type:way and highway=residential)",
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.FILTER_2,
                self.tr("Filter 2"),
                defaultValue="natural=tree",
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.timeout_input,
                "Timeout",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.data_aggregation_format,
                self.tr("Output Format"),
                options=self.formats,
                defaultValue=0,
            )
        )

        # Qgis internal
        advanced_parameters = [
            QgsProcessingParameterBoolean(
                self.check_show_metadata,
                self.tr("Show metadata"),
                defaultValue=False,
            ),
            QgsProcessingParameterBoolean(
                self.check_keep_geometryless,
                self.tr("Keep without geometry"),
                defaultValue=True,
            ),
            QgsProcessingParameterBoolean(
                self.check_merge_geometries,
                self.tr("Harmonize geometries"),
                defaultValue=True,
            ),
            QgsProcessingParameterBoolean(
                self.check_activate_temporal,
                self.tr("Qgis temporal feature"),
                defaultValue=True,
            ),
            QgsProcessingParameterBoolean(
                self.check_clip_geometry,
                self.tr("Clip geometry"),
                defaultValue=True,
            ),
        ]

        for param in advanced_parameters:
            param.setFlags(
                param.flags() | QgsProcessingParameterDefinition.FlagAdvanced
            )
            self.addParameter(param)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        layer = self.parameterAsLayer(parameters, self.LAYER, context)

        if layer.geometryType() == QgsWkbTypes.PointGeometry:
            geom = 1
        elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
            geom = 2

        if self.parameterAsBool(parameters, self.group_by_boundary, context):
            group_by_boundary_var = "/groupBy/boundary"
        else:
            group_by_boundary_var = ""

        preference = self.parameters[
            self.parameterAsInt(parameters, self.PARAMETER, context)
        ]

        processingParams = {
            "provider": self.parameterAsInt(parameters, self.PROVIDER, context),
            "geom": geom,
            "selection": "data-Aggregation",
            "preference": f"elements/{preference}/ratio{group_by_boundary_var}",
            "filter": self.parameterAsString(parameters, self.FILTER, context),
            "LAYER": self.parameterAsLayer(parameters, self.LAYER, context),
            "RADIUS": self.parameterAsInt(parameters, self.RADIUS, context),
            "date_start": self.parameterAsDateTime(
                parameters, self.date_start, context
            ),
            "date_end": self.parameterAsDateTime(
                parameters, self.date_end, context
            ),
            "timeout_input": self.parameterAsInt(
                parameters, self.timeout_input, context
            ),
            "preference_specification": "",
            "data_aggregation_format": "json",
            "check_show_metadata": self.parameterAsBool(
                parameters, self.check_show_metadata, context
            ),
            "timeout_input": self.parameterAsInt(
                parameters, self.timeout_input, context
            ),
            "data_aggregation_format": self.formats[
                self.parameterAsInt(
                    parameters, self.data_aggregation_format, context
                )
            ],
            "check_clip_geometry": self.parameterAsBool(
                parameters, self.check_clip_geometry, context
            ),
            "group_by_values_line_edit": self.parameterAsString(
                parameters, self.group_by_values_line_edit, context
            ),
            "group_by_key_line_edit": self.parameterAsString(
                parameters, self.group_by_key_line_edit, context
            ),
            "filter_2": self.parameterAsString(
                parameters, self.FILTER_2, context
            ),
            "filter": self.parameterAsString(parameters, self.FILTER, context),
            "period": self.parameterAsString(parameters, self.PERIOD, context),
            "output": self.parameterAsString(parameters, self.OUTPUT, context),
        }

        run_processing_alg(processingParams, feedback)

        # To run another Processing algorithm as part of this algorithm, you can use
        # processing.run(...). Make sure you pass the current context and feedback
        # to processing.run to ensure that all temporary layer outputs are available
        # to the executed algorithm, and that the executed algorithm can send feedback
        # reports to the user (and correctly handle cancellation and progress reports!)

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {"OUTPUT": self.OUTPUT}
