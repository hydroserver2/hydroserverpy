import requests
from typing import Optional
from hydroserverpy.core.endpoints import (DataLoaderEndpoint, DataSourceEndpoint, DatastreamEndpoint, ThingEndpoint,
                                          SensorEndpoint, UnitEndpoint, ProcessingLevelEndpoint,
                                          ObservedPropertyEndpoint, ResultQualifierEndpoint)


class HydroServer:
    """
    Connects to a HydroServer instance and used to interact with HydroServer's Data Management API endpoints.

    :param host: The base URL or host of the HydroServer API.
    :type host: str
    :param username: The username for basic authentication, if required.
    :type username: Optional[str]
    :param password: The password for basic authentication, if required.
    :type password: Optional[str]
    :param apikey: The API key for authentication, if using API key authentication.
    :type apikey: Optional[str]
    :param api_route: The API route to use, default is 'api'.
    :type api_route: str
    """

    def __init__(
            self,
            host: str,
            username: Optional[str] = None,
            password: Optional[str] = None,
            apikey: Optional[str] = None,
            api_route: str = 'api'
    ):
        self.host = host.strip('/')
        self.auth = (username or '__key__', password or apikey,) if (username and password) or apikey else None
        self.api_route = api_route.strip('/')
        self._session = None
        self._timeout = 60
        self._initialize_session()

    def _initialize_session(self) -> None:
        """
        The _initialize_session function is used to initialize the session object.

        :param self
        :return: None
        """

        if self._session is not None:
            self._session.close()

        self._session = requests.Session()

        if self.auth and self.auth[0] == '__key__':
            self._session.headers.update(
                {'key': self.auth[1]}
            )
        elif self.auth:
            self._session.auth = self.auth

    def _request(self, method, path, *args, **kwargs) -> requests.Response:
        """
        The _request function is a helper function that makes it easier to make requests to the API.
        It takes in a method, path, and any other arguments you want to pass into the request.
        The method argument should be one of 'get', 'post', or 'delete'. The path argument should be
        the endpoint you are trying to reach (e.g., '/users/me'). Any additional arguments will be passed
        into the request as-is.

        :param self
        :param method: Specify the type of request that is being made
        :param path: Specify the path of the request
        :return: A response object
        """

        for attempt in range(2):
            try:
                response = getattr(self._session, method)(
                    f'{self.host}/{path.strip("/")}',
                    timeout=self._timeout,
                    *args, **kwargs
                )
                response.raise_for_status()
                return response
            except requests.exceptions.ConnectionError as e:
                if attempt == 0:
                    self._initialize_session()
                    continue
                else:
                    raise e

    @property
    def dataloaders(self):
        """
        Data Loader Endpoint.

        :return: An instance of DataLoaderEndpoint.
        :rtype: DataLoaderEndpoint
        """

        return DataLoaderEndpoint(self)

    @property
    def datasources(self):
        """
        Data Source Endpoint.

        :return: An instance of DataSourceEndpoint.
        :rtype: DataSourceEndpoint
        """

        return DataSourceEndpoint(self)

    @property
    def datastreams(self):
        """
        Datastream Endpoint.

        :return: An instance of DatastreamEndpoint.
        :rtype: DatastreamEndpoint
        """

        return DatastreamEndpoint(self)

    @property
    def observedproperties(self):
        """
        Observed Property Endpoint.

        :return: An instance of ObservedPropertyEndpoint.
        :rtype: ObservedPropertyEndpoint
        """

        return ObservedPropertyEndpoint(self)

    @property
    def processinglevels(self):
        """
        Processing Level Endpoint.

        :return: An instance of ProcessingLevelEndpoint.
        :rtype: ProcessingLevelEndpoint
        """

        return ProcessingLevelEndpoint(self)

    @property
    def resultqualifiers(self):
        """
        Result Qualifier Endpoint.

        :return: An instance of ResultQualifierEndpoint.
        :rtype: ResultQualifierEndpoint
        """

        return ResultQualifierEndpoint(self)

    @property
    def sensors(self):
        """
        Sensor Endpoint.

        :return: An instance of SensorEndpoint.
        :rtype: SensorEndpoint
        """

        return SensorEndpoint(self)

    @property
    def things(self):
        """
        Thing Endpoint.

        :return: An instance of ThingEndpoint.
        :rtype: ThingEndpoint
        """

        return ThingEndpoint(self)

    @property
    def units(self):
        """
        Unit Endpoint.

        :return: An instance of UnitEndpoint.
        :rtype: UnitEndpoint
        """

        return UnitEndpoint(self)
