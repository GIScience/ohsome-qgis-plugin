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

import json
import random
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
from PyQt5.QtCore import QObject, pyqtSignal
from qgis._core import Qgis

from ohsomeTools import __version__
from ohsomeTools.common import networkaccessmanager
from ohsomeTools.utils import exceptions, logger
from ohsomeTools.utils.exceptions import ServiceUnavailable

_USER_AGENT = f"ohsome-qgis-plugin/{__version__}"


class Client(QObject):
    """Performs requests to the ohsome API services."""

    def __init__(self, provider=None, retry_timeout=60):
        """
        :param provider: An ohsome API provider from config.yml
        :type provider: dict

        :param retry_timeout: Timeout across multiple retryable requests, in
            seconds.
        :type retry_timeout: int
        """
        QObject.__init__(self)

        self.base_url = provider["base_url"]

        # self.session = requests.Session()
        # print('NetworkAccessManager')
        self.nam = networkaccessmanager.NetworkAccessManager(debug=False)

        self.retry_timeout = timedelta(seconds=retry_timeout)
        self.headers = {
            "User-Agent": _USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }

        # Save some references to retrieve in client instances
        self.url = None
        self.warnings = None
        self.canceled = False

    overQueryLimit = pyqtSignal()

    def request(
        self,
        url,
        params,
        first_request_time=None,
        retry_counter=0,
        post_json=None,
    ):
        """Performs HTTP GET/POST with credentials, returning the body as
        JSON.

        :param url: URL extension for request. Should begin with a slash.
        :type url: string

        :param params: HTTP GET parameters.
        :type params: dict or list of key/value tuples

        :param first_request_time: The time of the first request (None if no
            retries have occurred).
        :type first_request_time: datetime.datetime

        :param post_json: Parameters for POST endpoints
        :type post_json: dict

        :raises ohsomeTools.utils.exceptions.ApiError: when the API returns an error.

        :returns: ohsome API response body
        :rtype: dict
        """
        if not first_request_time:
            first_request_time = datetime.now()

        elapsed = datetime.now() - first_request_time
        if elapsed > self.retry_timeout:
            raise exceptions.Timeout()
        if retry_counter > 0:
            # 0.5 * (1.5 ^ i) is an increased sleep time of 1.5x per iteration,
            # starting at 0.5s when retry_counter=1. The first retry will occur
            # at 1, so subtract that first.
            delay_seconds = 1.5 ** (retry_counter - 1)
            # Jitter this value by 50% and pause.
            time.sleep(delay_seconds * (random.random() + 0.5))

        authed_url = self._generate_auth_url(
            url,
            params,
        )
        self.url = self.base_url + authed_url
        # Default to the client-level self.requests_kwargs, with method-level
        # requests_kwargs arg overriding.
        # final_requests_kwargs = self.requests_kwargs

        # Determine GET/POST
        # requests_method = self.session.get
        requests_method = "GET"
        body = None
        if post_json is not None:
            # requests_method = self.session.post
            # final_requests_kwargs["json"] = post_json
            body = post_json
            requests_method = "POST"

        logger.log(
            "url: {}\nParameters: {}".format(
                self.url,
                # final_requests_kwargs
                json.dumps(body, indent=2),
            ),
            0,
        )

        try:
            # response = requests_method(
            #     self.base_url + authed_url,
            #     **final_requests_kwargs
            # )
            response, content = self.nam.request(
                self.url,
                method=requests_method,
                body=body,
                headers=self.headers,
                blocking=True,
            )
        # except requests.exceptions.Timeout:
        #     raise exceptions.Timeout()
        except networkaccessmanager.RequestsExceptionTimeout:
            raise exceptions.Timeout

        except networkaccessmanager.RequestsException:
            try:
                # result = self._get_body(response)
                self._check_status()

            except exceptions.Unauthorized as e:
                # Let the instances know smth happened
                self.overQueryLimit.emit()
                logger.log("{}: {}".format(e.__class__.__name__, str(e)), 1)

                return self.request(
                    url,
                    params,
                    first_request_time,
                    retry_counter + 1,
                    post_json,
                )

            except exceptions.GenericClientError as e:
                logger.log(
                    f"The filter caused the error class {e.__class__.__name__} and "
                    f"the following API error: {str(e)}",
                    2,
                )
                raise e
            raise
        # print('request 1 done')
        return json.loads(content.decode("utf-8"))

    def _check_status(self):
        """
        Casts JSON response to dict
        :raises ohsomeTools.utils.exceptions.BadRequest
        :raises ohsomeTools.utils.exceptions.Unauthorized
        :raises ohsomeTools.utils.exceptions.NotFound
        :raises ohsomeTools.utils.exceptions.MethodNotAllowed
        :raises ohsomeTools.utils.exceptions.PayloadTooLarge
        :raises ohsomeTools.utils.exceptions.GenericClientError
        :raises ohsomeTools.utils.exceptions.InternalServerError
        :raises ohsomeTools.utils.exceptions.NotImplemented
        :raises ohsomeTools.utils.exceptions.ServiceUnavailable
        :raises ohsomeTools.utils.exceptions.GenericServerError
        :raises ohsomeTools.utils.exceptions.GenericServerError

        :returns: response body
        :rtype: dict
        """

        status_code = self.nam.http_call_result.status_code
        message = (
            self.nam.http_call_result.text
            if self.nam.http_call_result.text != ""
            else self.nam.http_call_result.reason
        )
        if message == "Network error: Connection refused":
            raise exceptions.ServiceUnavailable(
                str(status_code),
                # error,
                message
                + f". Check your internet connection or if your local ohsome API instance is running.",
            )
        if status_code == 400:
            raise exceptions.BadRequest(
                str(status_code),
                # error,
                message,
            )
        if status_code == 401:
            raise exceptions.Unauthorized(
                str(status_code),
                # error,
                message,
            )
        if status_code == 404:
            raise exceptions.NotFound(
                str(status_code),
                # error,
                message,
            )
        if status_code == 405:
            raise exceptions.MethodNotAllowed(
                str(status_code),
                # error,
                message,
            )
        if status_code == 413:
            raise exceptions.PayloadTooLarge(
                str(status_code),
                # error,
                message,
            )
        # Internal error message for Bad Request
        if 400 <= status_code < 500:
            raise exceptions.GenericClientError(
                str(status_code),
                # error,
                message,
            )
        if status_code == 500:
            raise exceptions.InternalServerError(
                str(status_code),
                # error,
                message,
            )
        if status_code == 501:
            raise exceptions.NotImplemented(
                str(status_code),
                # error,
                message,
            )
        if status_code == 503:
            raise exceptions.ServiceUnavailable(
                str(status_code),
                # error,
                message,
            )
        # Internal error message for Bad Request
        if 500 <= status_code < 600:
            raise exceptions.GenericServerError(
                str(status_code),
                # error,
                message,
            )
        # Other HTTP errors have different formatting
        if status_code != 200:
            raise exceptions.GenericServerError(
                str(status_code),
                # error,
                message,
            )

    def check_api_metadata(self, iface) -> {}:
        try:
            return self.request(f"/metadata", {})
        except ServiceUnavailable as err:
            iface.messageBar().pushMessage(
                "Warning",
                f"Endpoint {self.url} not available. Check your internet connection or provider settings.",
                level=Qgis.Critical,
                duration=5,
            )
            return False
        except Exception as err:
            iface.messageBar().pushMessage(
                "Critical",
                f"Endpoint not healthy. Unknown error: {err}.",
                level=Qgis.Critical,
                duration=7,
            )
            return False

    def _generate_auth_url(self, path, params):
        """Returns the path and query string portion of the request URL, first
        adding any necessary parameters.

        :param path: The path portion of the URL.
        :type path: string

        :param params: URL parameters.
        :type params: dict or list of key/value tuples

        :returns: encoded URL
        :rtype: string
        """

        if type(params) is dict:
            params = sorted(dict(**params).items())

        # Only auto-add API key when using ORS. If own instance, API key must
        # be explicitly added to params
        # if self.key:
        #     params.append(("api_key", self.key))

        return path + "?" + requests.utils.unquote_unreserved(urlencode(params))

    def cancel(self):
        self.nam.abort()
        self.canceled = True
