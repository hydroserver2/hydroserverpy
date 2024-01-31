from typing import List
from uuid import UUID
from hydroserverpy.schemas.data_loaders import DataLoaderGetResponse, DataLoaderPostBody, DataLoaderPatchBody
from hydroserverpy.schemas.data_sources import DataSourceGetResponse


class DataLoader:

    def __init__(self, service):
        self._service = service

    def list(self):

        return self._service.get(
            'data-loaders',
            response_schema=List[DataLoaderGetResponse]
        )

    def list_data_sources(self, data_loader_id: UUID):

        return self._service.get(
            f'data-loaders/{data_loader_id}/data-sources',
            response_schema=List[DataSourceGetResponse]
        )

    def get(self, data_loader_id: UUID):

        return self._service.get(
            f'data-loaders/{str(data_loader_id)}',
            response_schema=DataLoaderGetResponse
        )

    def create(self, data_loader_body: DataLoaderPostBody):

        return self._service.post(
            f'data-loaders',
            headers={'Content-type': 'application/json'},
            data=data_loader_body.json(by_alias=True),
            response_schema=DataLoaderGetResponse
        )

    def update(self, data_loader_id: UUID, data_loader_body: DataLoaderPatchBody):

        return self._service.patch(
            f'data-loaders/{str(data_loader_id)}',
            headers={'Content-type': 'application/json'},
            data=data_loader_body.json(exclude_unset=True, by_alias=True),
            response_schema=DataLoaderGetResponse
        )

    def delete(self, data_loader_id: UUID):

        return self._service.delete(
            f'data-loaders/{str(data_loader_id)}'
        )

    def load_data(self, data_loader_id: str):

        data_sources_response = self.list_data_sources(data_loader_id=UUID(data_loader_id))

        if data_sources_response.data:
            data_sources = data_sources_response.data
        else:
            return None

        for data_source in data_sources:
            self._service.data_sources.load_data(data_source_id=data_source.id)
