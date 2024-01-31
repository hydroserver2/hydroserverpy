from typing import List
from uuid import UUID
from hydroserverpy.schemas.things import ThingGetResponse, ThingPostBody, \
     ThingPatchBody


class Thing:

    def __init__(self, service):
        self._service = service

    def list(self):

        return self._service.get(
            'things',
            response_schema=List[ThingGetResponse]
        )

    def get(self, thing_id: str):

        return self._service.get(
            f'things/{thing_id}',
            response_schema=ThingGetResponse
        )
    
    def create(self, thing_body: ThingPostBody):

        return self._service.post(
            f'things',
            headers={'Content-type': 'application/json'},
            data=thing_body.json(by_alias=True),
            response_schema=ThingGetResponse
        )

    def update(self, thing_id: UUID, thing_body: ThingPatchBody):

        return self._service.patch(
            f'things/{str(thing_id)}',
            headers={'Content-type': 'application/json'},
            data=thing_body.json(exclude_unset=True, by_alias=True),
            response_schema=ThingGetResponse
        )

    def delete(self, thing_id: UUID):

        return self._service.delete(
            f'things/{str(thing_id)}'
        )
