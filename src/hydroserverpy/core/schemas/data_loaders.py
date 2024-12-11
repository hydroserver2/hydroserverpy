from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID
from hydroserverpy.core.schemas.base import HydroServerCoreModel

if TYPE_CHECKING:
    from hydroserverpy.core.schemas.data_sources import DataSource


class DataLoaderFields(BaseModel):
    name: str = Field(
        ...,
        strip_whitespace=True,
        max_length=255,
        description="The name of the data loader.",
    )


class DataLoader(HydroServerCoreModel, DataLoaderFields):
    """
    A model representing a DataLoader, extending the core functionality of HydroServerCoreModel with additional
    properties and methods.

    :ivar _data_sources: A private attribute to cache the list of data sources associated with the DataLoader.
    """

    def __init__(self, _endpoint, _uid: Optional[UUID] = None, **data):
        """
        Initialize a DataLoader instance.

        :param _endpoint: The endpoint associated with the data loader.
        :type _endpoint: str
        :param _uid: The unique identifier for the data loader.
        :type _uid: Optional[UUID]
        :param data: Additional attributes for the data loader.
        """

        super().__init__(_endpoint=_endpoint, _uid=_uid, **data)
        self._data_sources = None

    @property
    def data_sources(self) -> List["DataSource"]:
        """
        The data sources associated with the data loader. If not already cached, fetch the data sources from the server.

        :return: A list of data sources associated with the data loader.
        :rtype: List[DataSource]
        """

        if self._data_sources is None:
            self._data_sources = self._endpoint.list_data_sources(uid=self.uid)

        return self._data_sources

    def refresh(self) -> None:
        """
        Refresh the data loader with the latest data from the server and update cached data sources.
        """

        entity = self._endpoint.get(uid=self.uid).model_dump(exclude=["uid"])
        self._original_data = entity
        self.__dict__.update(entity)
        if self._data_sources is not None:
            self._data_sources = self._endpoint.list_data_sources(uid=self.uid)

    def load_observations(self) -> None:
        """
        Load observations data from a local file or a remote URL into HydroServer using all data sources associated with
        this data loader.
        """

        for data_source in self.data_sources:
            data_source.load_observations()
