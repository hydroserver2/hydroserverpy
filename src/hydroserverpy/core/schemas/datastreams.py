from pydantic import BaseModel, Field
from pandas import DataFrame
from typing import Optional, Literal, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from hydroserverpy.core.schemas.base import HydroServerCoreModel

if TYPE_CHECKING:
    from hydroserverpy.core.schemas.things import Thing
    from hydroserverpy.core.schemas.data_sources import DataSource
    from hydroserverpy.core.schemas.sensors import Sensor
    from hydroserverpy.core.schemas.units import Unit
    from hydroserverpy.core.schemas.processing_levels import ProcessingLevel
    from hydroserverpy.core.schemas.observed_properties import ObservedProperty


class DatastreamFields(BaseModel):
    name: str = Field(
        ..., strip_whitespace=True, max_length=255,
        description='The name of the datastream.'
    )
    description: str = Field(
        ..., strip_whitespace=True,
        description='A description of the datastream.'
    )
    observation_type: str = Field(
        ..., strip_whitespace=True, max_length=255,
        description='The type of observation recorded in this datastream'
    )
    sampled_medium: str = Field(
        ..., strip_whitespace=True, max_length=255,
        description='The physical medium in which the observations were sampled.'
    )
    no_data_value: float = Field(
        ...,
        description='A numerical value representing no data at a given timestamp.',
    )
    aggregation_statistic: str = Field(
        ..., strip_whitespace=True, max_length=255,
        description='The statistic calculated over the time aggregation interval of observations in this datastream.'
    )
    time_aggregation_interval: float = Field(
        ...,
        description='The time interval over which the aggregation statistic is applied to observations.',
    )
    status: Optional[str] = Field(
        None, strip_whitespace=True, max_length=255,
        description='The current status of this datastream.'
    )
    result_type: str = Field(
        ..., strip_whitespace=True, max_length=255,
        description='The type of result recorded in this datastream.'
    )
    value_count: Optional[int] = Field(
        None, ge=0,
        description='The total number of observations in this datastream.'
    )
    phenomenon_begin_time: Optional[datetime] = Field(
        None,
        description='The timestamp representing when the first phenomenon recorded in this datastream occurred.'
    )
    phenomenon_end_time: Optional[datetime] = Field(
        None,
        description='The timestamp representing when the last phenomenon recorded in this datastream occurred.'
    )
    result_begin_time: Optional[datetime] = Field(
        None,
        description='The timestamp representing when the first observation of this datastream was recorded.'
    )
    result_end_time: Optional[datetime] = Field(
        None,
        description='The timestamp representing when the last observation of this datastream was recorded.'
    )
    data_source_id: Optional[UUID] = Field(
        None,
        description='The data source for observations of this datastream.'
    )
    data_source_column: Optional[str] = Field(
        None, strip_whitespace=True, max_length=255,
        description='The name of the column containing this datastream\'s observations in the data source file.'
    )
    is_visible: bool = Field(
        True,
        description='Whether this datastream is publicly visible.'
    )
    is_data_visible: bool = Field(
        True,
        description='Whether this observations associated with this datastream are publicly visible.'
    )
    thing_id: UUID = Field(
        ...,
        description='The site/thing from which observations of this datastream were recorded.'
    )
    sensor_id: UUID = Field(
        ...,
        description='The sensor used to record observations of this datastream.'
    )
    observed_property_id: UUID = Field(
        ...,
        description='The physical property being observed for this datastream.'
    )
    processing_level_id: UUID = Field(
        ...,
        description='The processing level applied to this datastream.'
    )
    unit_id: UUID = Field(
        ...,
        description='The unit used to record observations for this datastream.'
    )
    time_aggregation_interval_units: Literal['seconds', 'minutes', 'hours', 'days'] = Field(
        ...,
        description='The time unit for this datastream\'s time aggregation interval'
    )
    intended_time_spacing: Optional[float] = Field(
        None,
        description='The time interval at which observations should be made for this datastream.'
    )
    intended_time_spacing_units: Optional[Literal['seconds', 'minutes', 'hours', 'days']] = Field(
        None,
        description='The time unit for this datastream\'s intended time spacing interval'
    )


class Datastream(HydroServerCoreModel, DatastreamFields):
    """
    A model representing a datastream, extending the core functionality of HydroServerCoreModel with additional
    properties and methods.

    :ivar _thing: A private attribute to cache the associated thing entity.
    :ivar _data_source: A private attribute to cache the associated data source entity.
    :ivar _observed_property: A private attribute to cache the associated observed property entity.
    :ivar _processing_level: A private attribute to cache the associated processing level entity.
    :ivar _unit: A private attribute to cache the associated unit entity.
    :ivar _sensor: A private attribute to cache the associated sensor entity.
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
        The thing entity associated with the datastream. If not already cached, fetch it from the server.

        :return: The thing entity associated with the datastream.
        :rtype: Thing
        """

        if self._thing is None:
            self._thing = self._endpoint._service.things.get(uid=self.thing_id)  # noqa

        return self._thing

    @property
    def data_source(self) -> 'DataSource':
        """
        The data source entity associated with the datastream. If not already cached, fetch it from the server.

        :return: The data source entity associated with the datastream.
        :rtype: DataSource
        """

        if self._data_source is None:
            self._data_source = self._endpoint._service.datasources.get(uid=self.data_source_id)  # noqa

        return self._data_source

    @property
    def observed_property(self) -> 'ObservedProperty':
        """
        Retrieve the observed property entity associated with the datastream. If not already cached, fetch it from the
        server.

        :return: The observed property entity associated with the datastream.
        :rtype: ObservedProperty
        """

        if self._observed_property is None:
            self._observed_property = self._endpoint._service.observedproperties.get(uid=self.observed_property_id)  # noqa

        return self._observed_property

    @property
    def processing_level(self) -> 'ProcessingLevel':
        """
        Retrieve the processing level entity associated with the datastream. If not already cached, fetch it from the
        server.

        :return: The processing level entity associated with the datastream.
        :rtype: ProcessingLevel
        """

        if self._processing_level is None:
            self._processing_level = self._endpoint._service.processinglevels.get(uid=self.processing_level_id)  # noqa

        return self._processing_level

    @property
    def unit(self) -> 'Unit':
        """
        Retrieve the unit entity associated with the datastream. If not already cached, fetch it from the server.

        :return: The unit entity associated with the datastream.
        :rtype: Unit
        """

        if self._unit is None:
            self._unit = self._endpoint._service.units.get(uid=self.unit_id)  # noqa

        return self._unit

    @property
    def sensor(self) -> 'Sensor':
        """
        Retrieve the sensor entity associated with the datastream. If not already cached, fetch it from the server.

        :return: The sensor entity associated with the datastream.
        :rtype: Any
        """

        if self._sensor is None:
            self._sensor = self._endpoint._service.sensors.get(uid=self.sensor_id)  # noqa

        return self._sensor

    def refresh(self) -> None:
        """
        Refresh the datastream with the latest data from the server and update cached entities if they were previously
        loaded.
        """

        entity = self._endpoint.get(uid=self.uid).model_dump(exclude=['uid'])
        self._original_data = entity
        self.__dict__.update(entity)
        if self._thing is not None:
            self._thing = self._endpoint._service.things.get(uid=self.thing_id)  # noqa
        if self._data_source is not None:
            self._data_source = self._endpoint._service.datasources.get(uid=self.data_source_id)  # noqa
        if self._observed_property is not None:
            self._observed_property = self._endpoint._service.observedproperties.get(uid=self.observed_property_id)  # noqa
        if self._processing_level is not None:
            self._processing_level = self._endpoint._service.processinglevels.get(uid=self.processing_level_id)  # noqa
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
        Retrieve the observations for this datastream.

        :return: A DataFrame containing the observations associated with the datastream.
        :rtype: DataFrame
        """

        return self._endpoint.get_observations(
            uid=self.uid, start_time=start_time, end_time=end_time, page=page, page_size=page_size,
            include_quality=include_quality, fetch_all=fetch_all
        )

    def load_observations(
            self,
            observations: DataFrame,
    ) -> None:
        """
        Load a DataFrame of observations to the datastream.

        :param observations: A pandas DataFrame containing the observations to be uploaded.
        :type observations: DataFrame
        :return: None
        """

        return self._endpoint.load_observations(
            uid=self.uid,
            observations=observations,
        )
