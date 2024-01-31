from typing import Optional, Union, Tuple
from pydantic import AnyHttpUrl
from hydroserverpy.service import BaseService
from hydroserverpy.components import DataLoader, DataSource, Datastream, ObservedProperty, ProcessingLevel, \
     ResultQualifier, Sensor, Thing, Unit, User


class HydroServer(BaseService):

    def __init__(
            self,
            host: Union[AnyHttpUrl, str],
            auth: Optional[Tuple[str, str]] = None,
            sta_path: str = 'api/sensorthings/v1.1',
            api_path: str = 'api/data'
    ):
        super().__init__(
            host=host,
            auth=auth,
            sta_path=sta_path,
            api_path=api_path
        )

    @property
    def data_loaders(self):
        return DataLoader(self)

    @property
    def data_sources(self):
        return DataSource(self)

    @property
    def datastreams(self):
        return Datastream(self)

    @property
    def observed_properties(self):
        return ObservedProperty(self)

    @property
    def processing_levels(self):
        return ProcessingLevel(self)

    @property
    def result_qualifiers(self):
        return ResultQualifier(self)

    @property
    def sensors(self):
        return Sensor(self)

    @property
    def things(self):
        return Thing(self)

    @property
    def units(self):
        return Unit(self)

    @property
    def users(self):
        return User(self)
