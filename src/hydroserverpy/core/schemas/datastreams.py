from pydantic import BaseModel, Field, StringConstraints as StrCon
from pandas import DataFrame
from typing import Optional, Literal, Annotated, Union, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from .base import HydroServerCoreModel

if TYPE_CHECKING:
    from .things import Thing
    from .data_sources import DataSource
    from .sensors import Sensor
    from .units import Unit
    from .processing_levels import ProcessingLevel
    from .observed_properties import ObservedProperty


class DatastreamFields(BaseModel):
    name: Union[UUID, Annotated[str, StrCon(strip_whitespace=True, max_length=255)]]
    description: Annotated[str, StrCon(strip_whitespace=True)]
    observation_type: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    sampled_medium: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    no_data_value: float
    aggregation_statistic: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    time_aggregation_interval: float
    status: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    result_type: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    value_count: Optional[Annotated[int, Field(ge=0)]] = None
    phenomenon_begin_time: Optional[datetime] = None
    phenomenon_end_time: Optional[datetime] = None
    result_begin_time: Optional[datetime] = None
    result_end_time: Optional[datetime] = None
    data_source_id: Optional[UUID] = None
    data_source_column: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    is_visible: bool = True
    is_data_visible: bool = True
    thing_id: UUID
    sensor_id: UUID
    observed_property_id: UUID
    processing_level_id: UUID
    unit_id: UUID
    time_aggregation_interval_units: Literal['seconds', 'minutes', 'hours', 'days']
    intended_time_spacing: Optional[float] = None
    intended_time_spacing_units: Optional[Literal['seconds', 'minutes', 'hours', 'days']] = None


class Datastream(HydroServerCoreModel, DatastreamFields):
    """
    A model representing a Datastream, extending the core functionality of HydroServerCoreModel with additional
    properties and methods.

    :ivar _thing: A private attribute to cache the associated Thing entity.
    :ivar _data_source: A private attribute to cache the associated Data Source entity.
    :ivar _observed_property: A private attribute to cache the associated Observed Property entity.
    :ivar _processing_level: A private attribute to cache the associated Processing Level entity.
    :ivar _unit: A private attribute to cache the associated Unit entity.
    :ivar _sensor: A private attribute to cache the associated Sensor entity.
    """

    def __init__(self, _endpoint, _uid: Optional[UUID] = None, **data):
        """
        Initialize a Datastream instance.

        :param _endpoint: The endpoint associated with the Datastream.
        :param _uid: The unique identifier for the Datastream.
        :type _uid: Optional[UUID]
        :param data: Additional attributes for the Datastream.
        """

        super().__init__(_endpoint=_endpoint, _uid=_uid, **data)
        self._thing = None
        self._data_source = None
        self._observed_property = None
        self._processing_level = None
        self._unit = None
        self._sensor = None

    @property
    def thing(self) -> 'Thing':
        """
        The Thing entity associated with the Datastream. If not already cached, fetch it from the server.

        :return: The Thing entity associated with the Datastream.
        :rtype: Thing
        """

        if self._thing is None:
            self._thing = self._endpoint._service.things.get(uid=self.thing_id)  # noqa

        return self._thing

    @property
    def data_source(self) -> 'DataSource':
        """
        The Data Source entity associated with the Datastream. If not already cached, fetch it from the server.

        :return: The Data Source entity associated with the Datastream.
        :rtype: DataSource
        """

        if self._data_source is None:
            self._data_source = self._endpoint._service.data_sources.get(uid=self.data_source_id)  # noqa

        return self._data_source

    @property
    def observed_property(self) -> 'ObservedProperty':
        """
        Retrieve the Observed Property entity associated with the Datastream. If not already cached, fetch it from the
        server.

        :return: The Observed Property entity associated with the Datastream.
        :rtype: ObservedProperty
        """

        if self._observed_property is None:
            self._observed_property = self._endpoint._service.observed_properties.get(uid=self.observed_property_id)  # noqa

        return self._observed_property

    @property
    def processing_level(self) -> 'ProcessingLevel':
        """
        Retrieve the Processing Level entity associated with the Datastream. If not already cached, fetch it from the
        server.

        :return: The Processing Level entity associated with the Datastream.
        :rtype: ProcessingLevel
        """

        if self._processing_level is None:
            self._processing_level = self._endpoint._service.processing_levels.get(uid=self.processing_level_id)  # noqa

        return self._processing_level

    @property
    def unit(self) -> 'Unit':
        """
        Retrieve the Unit entity associated with the Datastream. If not already cached, fetch it from the server.

        :return: The Unit entity associated with the Datastream.
        :rtype: Unit
        """

        if self._unit is None:
            self._unit = self._endpoint._service.units.get(uid=self.unit_id)  # noqa

        return self._unit

    @property
    def sensor(self) -> 'Sensor':
        """
        Retrieve the Sensor entity associated with the Datastream. If not already cached, fetch it from the server.

        :return: The Sensor entity associated with the Datastream.
        :rtype: Any
        """

        if self._sensor is None:
            self._sensor = self._endpoint._service.sensors.get(uid=self.sensor_id)  # noqa

        return self._sensor

    def refresh(self) -> None:
        """
        Refresh the Datastream with the latest data from the server and update cached entities if they were previously
        loaded.
        """

        entity = self._endpoint.get(uid=self.uid).model_dump(exclude=['uid'])
        self._original_data = entity
        self.__dict__.update(entity)
        if self._thing is not None:
            self._thing = self._endpoint._service.things.get(uid=self.thing_id)  # noqa
        if self._data_source is not None:
            self._data_source = self._endpoint._service.data_sources.get(uid=self.data_source_id)  # noqa
        if self._observed_property is not None:
            self._observed_property = self._endpoint._service.observed_properties.get(uid=self.observed_property_id)  # noqa
        if self._processing_level is not None:
            self._processing_level = self._endpoint._service.processing_levels.get(uid=self.processing_level_id)  # noqa
        if self._unit is not None:
            self._unit = self._endpoint._service.units.get(uid=self.unit_id)  # noqa
        if self._sensor is not None:
            self._sensor = self._endpoint._service.sensors.get(uid=self.sensor_id)  # noqa

    def get_observations(
            self,
            start_time: datetime = None,
            end_time: datetime = None,
            page: int = 1,
            page_size: int = 100000,
            include_quality: bool = False,
            fetch_all: bool = False
    ) -> DataFrame:
        """
        Retrieve the observations for this Datastream.

        :return: A DataFrame containing the observations associated with the Datastream.
        :rtype: DataFrame
        """

        return self._endpoint.get_observations(
            uid=self.uid, start_time=start_time, end_time=end_time, page=page, page_size=page_size,
            include_quality=include_quality, fetch_all=fetch_all
        )

    def upload_observations(
            self,
            observations: DataFrame,
    ) -> None:
        """
        Upload a DataFrame of observations to the Datastream.

        :param observations: A pandas DataFrame containing the observations to be uploaded.
        :type observations: DataFrame
        :return: None
        """

        return self._endpoint.upload_observations(
            uid=self.uid,
            observations=observations,
        )
