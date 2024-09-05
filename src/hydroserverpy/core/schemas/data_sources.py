from pydantic import BaseModel, Field, StringConstraints as StrCon
from typing import Optional, Literal, Annotated, Union, List, TYPE_CHECKING
from datetime import datetime
from uuid import UUID
from .base import HydroServerCoreModel

if TYPE_CHECKING:
    from .data_loaders import DataLoader
    from .datastreams import Datastream


class DataSourceFields(BaseModel):
    name: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    path: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    link: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    header_row: Optional[Annotated[int, Field(gt=0, lt=9999)]] = None
    data_start_row: Optional[Annotated[int, Field(gt=0, lt=9999)]] = 1
    delimiter: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=1)]] = ','
    quote_char: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=1)]] = '"'
    interval: Optional[Annotated[int, Field(gt=0, lt=9999)]] = None
    interval_units: Optional[Literal['minutes', 'hours', 'days', 'weeks', 'months']] = None
    crontab: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    paused: Optional[bool]
    timestamp_column: Union[
        Annotated[int, Field(gt=0, lt=9999)], Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    ]
    timestamp_format: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = '%Y-%m-%dT%H:%M:%S%Z'
    timestamp_offset: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = '+0000'
    data_loader_id: UUID
    data_source_thru: Optional[datetime] = None
    last_sync_successful: Optional[bool] = None
    last_sync_message: Optional[Annotated[str, StrCon(strip_whitespace=True)]] = None
    last_synced: Optional[datetime] = None
    next_sync: Optional[datetime] = None


class DataSource(HydroServerCoreModel, DataSourceFields):
    """
    A model representing a DataSource, extending the core functionality of HydroServerCoreModel with additional
    properties and methods.

    :ivar _datastreams: A private attribute to cache the list of datastreams associated with the DataSource.
    :ivar _data_loader: A private attribute to cache the DataLoader associated with the DataSource.
    """

    def __init__(self, _endpoint, _uid: Optional[UUID] = None, **data):
        """
        Initialize a DataSource instance.

        :param _endpoint: The endpoint associated with the DataSource.
        :param _uid: The unique identifier for the DataSource.
        :type _uid: Optional[UUID]
        :param data: Additional attributes for the DataSource.
        """

        super().__init__(_endpoint=_endpoint, _uid=_uid, **data)
        self._datastreams = None
        self._data_loader = None

    @property
    def datastreams(self) -> List['Datastream']:
        """
        Retrieve the datastreams associated with the DataSource. If not already cached, fetch the datastreams from the
        server.

        :return: A list of datastreams associated with the DataSource.
        :rtype: List[Datastream]
        """

        if self._datastreams is None:
            self._datastreams = self._endpoint.list_datastreams(uid=self.uid)

        return self._datastreams

    @property
    def data_loader(self) -> 'DataLoader':
        """
        Retrieve the DataLoader associated with the DataSource. If not already cached, fetch the DataLoader from the
        server.

        :return: The DataLoader associated with the DataSource.
        :rtype: DataLoader
        """

        if self._data_loader is None:
            self._data_loader = self._endpoint._service.dataloaders.get(uid=self.data_loader_id)  # noqa
        return self._data_loader

    def refresh(self) -> None:
        """
        Refresh the DataSource with the latest data from the server and update cached datastreams and DataLoader if they
        were previously loaded.
        """

        entity = self._endpoint.get(uid=self.uid).model_dump(exclude=['uid'])
        self._original_data = entity
        self.__dict__.update(entity)
        if self._datastreams is not None:
            self._datastreams = self._endpoint.list_datastreams(uid=self.uid)
        if self._data_loader is not None:
            self._data_loader = self._endpoint._service.dataloaders.get(uid=self.data_loader_id)  # noqa
