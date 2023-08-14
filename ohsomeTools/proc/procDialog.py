from ohsomeTools.utils import (
    logger,
    configmanager,
)

import json
from datetime import datetime
from PyQt5.QtWidgets import QDialogButtonBox, QMessageBox
from qgis._core import (
    QgsVectorLayer,
    Qgis,
    QgsProcessingUtils,
)

from ohsomeTools.common import client, request_core
from ohsomeTools.utils import exceptions, logger
from qgis.utils import iface
from ohsomeTools.gui import ohsome_spec

def run_processing_alg(processingParams):


    # Clean the debug text
    try:
        provider_id = 0 # Muss in combo box noch zugänglich gemacht werden.
        provider = configmanager.read_config()["providers"][provider_id]
    except IndexError:
        msg = "Request aborted. No provider available. Please check your provider list.\n"
        logger.log(msg, 1)
        iface.messageBar().pushMessage(
            "Warning",
            msg,
            level=Qgis.Warning,
            duration=5,
        )
        return

    clnt = client.Client(provider)

    metadata_check = clnt.check_api_metadata(iface)

    # get preferences from dialog
    preferences = ohsome_spec.ProcessingOhsomeSpec(params=processingParams)

    try:
        '''if not metadata_check or not preferences.is_valid(False):
            msg = "The request has been aborted!"
            logger.log(msg, 0)
            return'''

        # if there are no centroids or layers, throw an error message
        geom = processingParams['geom']
        if (
                processingParams['selection']
                == "metadata"
        ):
            request(clnt, preferences, processingParams)

        elif geom == 1:
            layer_preferences = (
                preferences.get_point_layer_request_preferences()
            )
            if not len(layer_preferences):
                return

            for point_layer_preference in layer_preferences:

                request(clnt, preferences, processingParams, point_layer_preference)

        elif geom == 2:
            logger.log('polygon')
            layer_preferences = (
                preferences.get_polygon_layer_request_preferences()
            )
            for polygon_layer_preference in layer_preferences:
                logger.log('iteration')
                request(clnt, preferences, processingParams, polygon_layer_preference)
        else:
            return

    except exceptions.TooManyInputsFound as e:
        msg = [e.__class__.__name__, str(e)]
        logger.log("{}: {}".format(*msg), 2)
        iface.messageBar().pushMessage(
            "Error",
            "Request aborted. Layer input name is not unique.",
            level=Qgis.Critical,
            duration=5,
        )
    except Exception as e:
        msg = [e.__class__.__name__, str(e)]
        logger.log("{}: {}".format(*msg), 2)
        iface.messageBar().pushMessage(
            "Error",
            "Request aborted. Check the tool log.",
            level=Qgis.Critical,
            duration=5,
        )
    finally:
        if not metadata_check:
            return True
        elif not preferences.is_valid(True):
            iface.messageBar().pushMessage(
                "Warning",
                "Preferences are not valid. Check the plugin log.",
                level=Qgis.Critical,
                duration=7,
            )
            return
    logger.log('run_processing_alg done')

def request(clnt, preferences, parameters, point_layer_preference={}):
    logger.log('requesting')
    try:
        request_time = datetime.now().strftime("%m-%d-%Y:%H-%M-%S")
        if len(point_layer_preference):
            logger.log('requesting 1')
            result = clnt.request(
                f"/{preferences.get_request_url()}",
                {},
                post_json=point_layer_preference,
            )
        else:
            logger.log('meta')
            result = client.request(f"/metadata", {})
    except Exception as e:
        logger.log(str(e))
        result = None
        logger.log(e)

    logger.log('postprocessing')
    if not result or not len(result):
        logger.log('postdbabd')
        return False
    logger.log('postprocessing2')
    if "extractRegion" in result:
        logger.log('extractRegion')
        vlayer: QgsVectorLayer = iface.addVectorLayer(
            json.dumps(
                result.get("extractRegion").get("spatialExtent")
            ),
            f"OHSOME_API_spatial_extent",
            "ogr",
        )
        if vlayer:
            return True
    elif (
            all(i in result.keys() for i in ["type", "features"])
            and result.get("type").lower() == "featurecollection"
    ):
        # Process GeoJSON
        logger.log('GeoJson')
        geojsons: [] = request_core.split_geojson_by_geometry(
            result,
            keep_geometry_less=parameters['check_keep_geometryless'],
            combine_single_with_multi_geometries=parameters['check_merge_geometries'],
        )
        for i in range(len(geojsons)):
            vlayer = request_core.create_ohsome_vector_layer(
                iface,
                geojsons[i],
                request_time,
                preferences.get_request_url(),
                parameters['check_activate_temporal'],
            )
            request_core.postprocess_metadata(geojsons[i], vlayer)
        return True
    elif (
            "result" in result.keys()
            and len(result.get("result")) > 0
    ):
        # Process flat tables
        file = QgsProcessingUtils.generateTempFilename(
            f"{preferences.get_request_url()}.csv"
        )
        header = result["result"][0].keys()
        vlayer = request_core.create_ohsome_csv_layer(
            iface,
            result["result"],
            header,
            file,
            request_time,
        )
        request_core.postprocess_metadata(result, vlayer)
        return True
    elif (
            "groupByResult" in result.keys()
            and len(result.get("groupByResult")) > 0
    ):
        # Process non-flat tables
        logger.log('non-flat tables')
        results = result["groupByResult"]
        for result_group in results:
            file = QgsProcessingUtils.generateTempFilename(
                f'{result_group["groupByObject"]}_{preferences.get_request_url()}.csv'
            )
            header = results[0]["result"][0].keys()
            vlayer = request_core.create_ohsome_csv_layer(
                iface,
                result_group["result"],
                header,
                file,
                request_time,
            )
            request_core.postprocess_metadata(result, vlayer)
        return True
    elif (
            "ratioResult" in result.keys()
            and len(result.get("ratioResult")) > 0
    ):
        # Process flat tables
        file = QgsProcessingUtils.generateTempFilename(
            f"{preferences.get_request_url()}.csv"
        )
        header = result.get("ratioResult")[0].keys()
        vlayer = request_core.create_ohsome_csv_layer(
            iface,
            result["ratioResult"],
            header,
            file,
            request_time,
        )
        request_core.postprocess_metadata(result, vlayer)
        return True
    logger.log('postprocessing done')
    return False
