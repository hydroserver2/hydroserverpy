import tempfile
import io
from pydantic import BaseModel, Field
from typing import Optional, Literal, Union, List, TYPE_CHECKING
from datetime import datetime
from uuid import UUID
from urllib.request import urlopen
from hydroserverpy.core.schemas.base import HydroServerCoreModel
from hydroserverpy.etl_csv.hydroserver_etl_csv import HydroServerETLCSV

if TYPE_CHECKING:
    from hydroserverpy.core.schemas.data_loaders import DataLoader
    from hydroserverpy.core.schemas.datastreams import Datastream


class DataSourceFields(BaseModel):
    name: str = Field(
        ...,
        strip_whitespace=True,
        max_length=255,
        description="The name of the data source.",
    )
    path: Optional[str] = Field(
        None,
        strip_whitespace=True,
        max_length=255,
        description="The path to a local data source file.",
    )
    link: Optional[str] = Field(
        None,
        strip_whitespace=True,
        max_length=255,
        description="The link to a remote data source file.",
    )
    header_row: Optional[int] = Field(
        None, gt=0, lt=9999, description="The row number where the data begins."
    )
    data_start_row: Optional[int] = Field(
        None, gt=0, lt=9999, description="The row number where the data begins."
    )
    delimiter: Optional[str] = Field(
        ",",
        strip_whitespace=True,
        max_length=1,
        description="The delimiter used by the data source file.",
    )
    quote_char: Optional[str] = Field(
        '"',
        strip_whitespace=True,
        max_length=1,
        description="The quote delimiter character used by the data source file.",
    )
    interval: Optional[int] = Field(
        None,
        gt=0,
        lt=9999,
        description="The time interval at which the data source should be loaded.",
    )
    interval_units: Optional[Literal["minutes", "hours", "days", "weeks", "months"]] = (
        Field(None, description="The interval units used by the data source file.")
    )
    crontab: Optional[str] = Field(
        None,
        strip_whitespace=True,
        max_length=255,
        description="The crontab used to schedule when the data source should be loaded.",
    )
    start_time: Optional[datetime] = Field(
        None, description="When the data source should begin being loaded."
    )
    end_time: Optional[datetime] = Field(
        None, description="When the data source should stop being loaded."
    )
    paused: Optional[bool] = Field(
        False, description="Whether loading the data source should be paused or not."
    )
    timestamp_column: Union[int, str] = Field(
        ...,
        strip_whitespace=True,
        max_length=255,
        description="The column of the data source file containing the timestamps.",
    )
    timestamp_format: Optional[str] = Field(
        "%Y-%m-%dT%H:%M:%S%Z",
        strip_whitespace=True,
        max_length=255,
        description="The format of the timestamps, using Python's datetime strftime codes.",
    )
    timestamp_offset: Optional[str] = Field(
        "+0000",
        strip_whitespace=True,
        max_length=255,
        description="An ISO 8601 time zone offset designator code to be applied to timestamps in the data source file.",
    )
    data_loader_id: UUID = Field(
        ...,
        description="The ID of the data loader responsible for loading this data source.",
    )
    data_source_thru: Optional[datetime] = Field(
        None, description="The timestamp through which the data source contains data."
    )
    last_sync_successful: Optional[bool] = Field(
        None, description="Whether the last data loading attempt was successful of not."
    )
    last_sync_message: Optional[str] = Field(
        None,
        strip_whitespace=True,
        description="A message generated by the data loader it attempted to load data from this data source.",
    )
    last_synced: Optional[datetime] = Field(
        None,
        description="The last time the data loader attempted to load data from this data source.",
    )
    next_sync: Optional[datetime] = Field(
        None,
        description="The next time the data loader will attempt to load data from this data source.",
    )


class DataSource(HydroServerCoreModel, DataSourceFields):
    """
    A model representing a data source, extending the core functionality of HydroServerCoreModel with additional
    properties and methods.

    :ivar _datastreams: A private attribute to cache the list of datastreams associated with the data source.
    :ivar _data_loader: A private attribute to cache the data loader associated with the data source.
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
    def datastreams(self) -> List["Datastream"]:
        """
        Retrieve the datastreams associated with the DataSource. If not already cached, fetch the datastreams from the
        server.

        :return: A list of datastreams associated with the data source.
        :rtype: List[Datastream]
        """

        if self._datastreams is None:
            self._datastreams = self._endpoint.list_datastreams(uid=self.uid)

        return self._datastreams

    @property
    def data_loader(self) -> "DataLoader":
        """
        Retrieve the data loader associated with the data source. If not already cached, fetch the data loader from the
        server.

        :return: The data loader associated with the data source.
        :rtype: DataLoader
        """

        if self._data_loader is None:
            self._data_loader = self._endpoint._service.dataloaders.get(
                uid=self.data_loader_id
            )  # noqa

        return self._data_loader

    def refresh(self) -> None:
        """
        Refresh the data source with the latest data from the server and update cached datastreams and data loader if
        they were previously loaded.
        """

        entity = self._endpoint.get(uid=self.uid).model_dump(exclude=["uid"])
        self._original_data = entity
        self.__dict__.update(entity)
        if self._datastreams is not None:
            self._datastreams = self._endpoint.list_datastreams(uid=self.uid)
        if self._data_loader is not None:
            self._data_loader = self._endpoint._service.dataloaders.get(
                uid=self.data_loader_id
            )  # noqa

    def load_observations(self) -> None:
        """
        Load observations data from a local file or a remote URL into HydroServer using this data source configuration.
        """

        if self.path:
            with open(self.path, "rb") as f:
                with io.TextIOWrapper(f, encoding="utf-8") as data_file:
                    hs_etl = HydroServerETLCSV(
                        service=getattr(self._endpoint, "_service"),
                        data_file=data_file,
                        data_source=self,
                    )
                    hs_etl.run()
        elif self.link:
            with tempfile.NamedTemporaryFile(mode="w+b") as temp_file:
                with urlopen(self.link) as response:
                    chunk_size = 1024 * 1024 * 10  # Use a 10mb chunk size.
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        temp_file.write(chunk)
                temp_file.seek(0)
                with io.TextIOWrapper(temp_file, encoding="utf-8") as data_file:
                    hs_etl = HydroServerETLCSV(
                        service=getattr(self._endpoint, "_service"),
                        data_file=data_file,
                        data_source=self,
                    )
                    hs_etl.run()
        else:
            return None
