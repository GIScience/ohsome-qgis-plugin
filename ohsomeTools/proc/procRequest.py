import json
from datetime import datetime
from qgis._core import (
    QgsVectorLayer,
    QgsProcessingUtils,
    QgsProject
    )
from ohsomeTools.common import client, request_core
from ohsomeTools.utils import logger
from qgis.utils import iface


def processing_request(clnt, preferences, parameters, point_layer_preference={}):
    logger.log('requesting')
    try:
        request_time = datetime.now().strftime("%m-%d-%Y:%H-%M-%S")
        if len(point_layer_preference):
            logger.log('requesting 1')
            result = clnt.processing_request(
                f"/{preferences.get_request_url()}",
                {},
                post_json=point_layer_preference,
            )
        else:
            logger.log('meta')
            result = clnt.request(f"/metadata", {})
    except Exception as e:
        logger.log(str(e))
        result = None
        logger.log(e)

    logger.log('postprocessing')
    if not result or not len(result):
        logger.log('postdbabd')
        return False
    if "extractRegion" in result:
        logger.log('extractRegion')

        vlayer : QgsVectorLayer= QgsVectorLayer(
            json.dumps(
                result.get("extractRegion")
                .get("spatialExtent")),
                f"OHSOME_API_spatial_extent",
                "ogr")
        QgsProject.instance().addMapLayer(vlayer)
        logger.log('extractRegion2')
        if vlayer:
            logger.log('extractRegion3')
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
        logger.log('non-flat tables procDialog')
        results = result["groupByResult"]
        logger.log('debug1')
        logger.log(str(len(results)))
        for result_group in results:
            logger.log('debug2')
            file = QgsProcessingUtils.generateTempFilename(
                f'{result_group["groupByObject"]}_{preferences.get_request_url()}.csv'
            )
            header = results[0]["result"][0].keys()
            logger.log('debug3')
            vlayer = request_core.create_ohsome_csv_layer(
                iface,
                result_group["result"],
                header,
                file,
                request_time,
            )
            logger.log('debug4')
            request_core.postprocess_metadata(result, vlayer)
            print('debug5')
        print('debug6')
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