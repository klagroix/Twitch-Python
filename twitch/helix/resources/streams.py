from typing import Generator, Tuple, List, Optional

import twitch.helix as helix
from twitch.api import API
from .resource import Resource
import logging


logger = logging.getLogger(__name__)

USE_BEARER = False # helix API doesn't support using bearer for stream data. Need to disable for these API calls


class StreamNotFound(Exception):
    pass


class Streams(Resource['helix.Stream']):

    def __init__(self, api: API, ignore_cache: Optional[bool] = False, **kwargs):
        logger.debug("Streams - entering __init__")
        super().__init__(api=api, path='streams')

        # Store kwargs as class property for __iter__
        self._kwargs = kwargs

        response: dict = self._api.get(self._path, ignore_cache=ignore_cache, use_bearer=USE_BEARER, params=kwargs)

        if response['data']:
            self._data = [helix.Stream(api=self._api, data=video) for video in
                          response['data']]
        else:
            raise StreamNotFound('No stream was found')

    @property
    def users(self) -> Generator[Tuple['helix.Stream', 'helix.User'], None, None]:
        for stream in self:
            yield stream, stream.user

    def _can_paginate(self) -> bool:
        # print("DEBUGGING - streams.py: _can_paginate")
        return True

    def _handle_pagination_response(self, response: dict) -> List['helix.Stream']:
        """
        Custom handling for stream pagination
        :param response: API response data
        :return: Streams
        """

        # print("DEBUGGING - streams.py: _handle_pagination_response")
        streams: List['helix.Stream'] = [helix.Stream(api=self._api, data=stream) for stream in response['data']]

        return streams
