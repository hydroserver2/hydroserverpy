import requests
import json
import frost_sta_client as fsc
from typing import Optional, Union, Tuple
from pydantic import AnyHttpUrl


class BaseService:

    def __init__(
            self,
            host: Union[AnyHttpUrl, str],
            sta_path: str,
            api_path: str,
            auth: Optional[Tuple[str, str]] = None,
    ):
        self.host = host.strip('/')
        self.auth = auth
        self.sensorthings = None
        self._sta_path = sta_path.strip('/')
        self._api_path = api_path.strip('/')
        self._session = None
        self._timeout = 60
        self._initialize_session()

    def _initialize_session(self):
        if self._session is not None:
            self._session.close()

        self._session = requests.Session()

        if self.auth and self.auth[0] == '__token__':
            self._session.headers.update(
                {'Authorization': f'Bearer {self.auth[1]}'}
            )
        elif self.auth:
            self._session.auth = self.auth

        self.sensorthings = fsc.SensorThingsService(
            url=f'{self.host}/{self._sta_path}'
        )

    def _request(self, method, path, *args, **kwargs):
        for attempt in range(2):
            try:
                return getattr(self._session, method)(
                    f'{self.host}/{self._api_path}/{path.strip("/")}',
                    timeout=self._timeout,
                    *args, **kwargs
                )
            except requests.exceptions.ConnectionError as e:
                if attempt == 0:
                    self._initialize_session()
                    continue
                else:
                    raise e

    def get(self, path, *args, **kwargs):
        """
        The get function accepts a path and any other arguments that are passed to it,
        and then calls the _request function with the 'get' method. If the request is successful,
        the response content is parsed and added to the response object to be returned.

        :param self: Represent the instance of the class
        :param path: Specify the url of the request
        :return: A response object
        """

        response = self._request('get', path, *args, **kwargs)

        if response.status_code == 200:
            response.data = json.loads(response.content)
        else:
            response.data = None

        return response

    def post(self, path, *args, **kwargs):
        """
        The post function accepts a path and any other arguments that are passed to it,
        and then calls the _request function with the 'post' method. If the request is successful,
        the response content is parsed and added to the response object to be returned.

        :param self: Represent the instance of the class
        :param path: Specify the url of the request
        :return: A response object
        """

        response = self._request('post', path, *args, **kwargs)

        if response.status_code == 201:
            response.data = json.loads(response.content)
        else:
            response.data = None

        return response
