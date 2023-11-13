from uuid import UUID
from typing import List
from hydroserverpy.schemas.datastreams import DatastreamGetResponse, DatastreamPostBody, DatastreamPatchBody


class Datastream:

    def __init__(self, service):
        self._service = service

    def list(self):

        return self._service.get(
            'datastreams',
            response_schema=List[DatastreamGetResponse]
        )

    def get(self, datastream_id: str):

        return self._service.get(
            f'datastreams/{datastream_id}',
            response_schema=DatastreamGetResponse
        )

    def create(self, datastream_body: DatastreamPostBody):

        return self._service.post(
            f'datastreams',
            headers={'Content-type': 'application/json'},
            data=datastream_body.json(by_alias=True),
            response_schema=DatastreamGetResponse
        )

    def update(self, datastream_id: UUID, datastream_body: DatastreamPatchBody):

        return self._service.patch(
            f'datastreams/{str(datastream_id)}',
            headers={'Content-type': 'application/json'},
            data=datastream_body.json(exclude_unset=True, by_alias=True),
            response_schema=DatastreamGetResponse
        )

    def delete(self, datastream_id: UUID):

        return self._service.delete(
            f'datastreams/{str(datastream_id)}'
        )
