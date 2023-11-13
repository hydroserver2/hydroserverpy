import tempfile
from urllib.request import urlopen
from uuid import UUID
from typing import List
from hydroserverpy.schemas.data_sources import DataSourceGetResponse, DataSourcePostBody, DataSourcePatchBody
from hydroserverpy.schemas.datastreams import DatastreamGetResponse
from hydroserverpy.etl import HydroServerETL


class DataSource:

    def __init__(self, service):
        self._service = service

    def list(self):

        return self._service.get(
            'data-sources',
            response_schema=List[DataSourceGetResponse]
        )

    def list_datastreams(self, data_source_id: UUID):

        return self._service.get(
            f'data-sources/{data_source_id}/datastreams',
            response_schema=List[DatastreamGetResponse]
        )

    def get(self, data_source_id: UUID):

        return self._service.get(
            f'data-sources/{data_source_id}',
            response_schema=DataSourceGetResponse
        )

    def create(self, data_source_body: DataSourcePostBody):

        return self._service.post(
            f'data-sources',
            headers={'Content-type': 'application/json'},
            data=data_source_body.json(by_alias=True),
            response_schema=DataSourceGetResponse
        )

    def update(self, data_source_id: UUID, data_source_body: DataSourcePatchBody):
        return self._service.patch(
            f'data-sources/{str(data_source_id)}',
            headers={'Content-type': 'application/json'},
            data=data_source_body.json(exclude_unset=True, by_alias=True),
            response_schema=DataSourceGetResponse
        )

    def delete(self, data_source_id: UUID):

        return self._service.delete(
            f'data-sources/{str(data_source_id)}'
        )

    def load_data(self, data_source_id: UUID):

        data_source_response = self.get(data_source_id=data_source_id)

        if data_source_response.data:
            data_source = data_source_response.data
        else:
            return None

        datastreams_response = self.list_datastreams(data_source_id=data_source_id)
        datastreams = datastreams_response.data

        if data_source.path:
            with open(data_source.path) as data_file:
                hs_etl = HydroServerETL(
                    service=self._service,
                    data_file=data_file,
                    data_source=data_source,
                    datastreams=datastreams
                )
                hs_etl.run()
        elif data_source.url:
            with tempfile.NamedTemporaryFile(mode='w') as temp_file:
                with urlopen(data_source.url) as response:
                    chunk_size = 1024 * 1024 * 10  # Use a 10mb chunk size.
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        temp_file.write(chunk)
                temp_file.seek(0)
                hs_etl = HydroServerETL(
                    service=self._service,
                    data_file=temp_file,
                    data_source=data_source,
                    datastreams=datastreams
                )
                hs_etl.run()
        else:
            return None
