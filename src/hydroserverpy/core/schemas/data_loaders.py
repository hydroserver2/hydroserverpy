from pydantic import BaseModel, StringConstraints as StrCon
from typing import Annotated, Optional, List, TYPE_CHECKING
from uuid import UUID
from .base import HydroServerCoreModel

if TYPE_CHECKING:
    from .data_sources import DataSource


class DataLoaderFields(BaseModel):
    name: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]


class DataLoader(HydroServerCoreModel, DataLoaderFields):
    """
    A model representing a DataLoader, extending the core functionality of HydroServerCoreModel with additional
    properties and methods.

    :ivar _data_sources: A private attribute to cache the list of data sources associated with the DataLoader.
    """

    def __init__(self, _endpoint, _uid: Optional[UUID] = None, **data):
        """
        Initialize a DataLoader instance.

        :param _endpoint: The endpoint associated with the DataLoader.
        :param _uid: The unique identifier for the DataLoader.
        :type _uid: Optional[UUID]
        :param data: Additional attributes for the DataLoader.
        """

        super().__init__(_endpoint=_endpoint, _uid=_uid, **data)
        self._data_sources = None

    @property
    def data_sources(self) -> List['DataSource']:
        """
        The data sources associated with the DataLoader. If not already cached, fetch the data sources from the server.

        :return: A list of data sources associated with the DataLoader.
        :rtype: List[DataSource]
        """

        if self._data_sources is None:
            self._data_sources = self._endpoint.list_data_sources(uid=self.uid)

        return self._data_sources

    def refresh(self) -> None:
        """
        Refresh the DataLoader with the latest data from the server and update cached data sources.
        """

        entity = self._endpoint.get(uid=self.uid).model_dump(exclude=['uid'])
        self._original_data = entity
        self.__dict__.update(entity)
        if self._data_sources is not None:
            self._data_sources = self._endpoint.list_data_sources(uid=self.uid)
