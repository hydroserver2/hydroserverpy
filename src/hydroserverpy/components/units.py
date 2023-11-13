from typing import List
from uuid import UUID
from hydroserverpy.schemas.units import UnitGetResponse, UnitPostBody, \
     UnitPatchBody


class Unit:

    def __init__(self, service):
        self._service = service

    def list(self):

        return self._service.get(
            'units',
            response_schema=List[UnitGetResponse]
        )

    def get(self, unit_id: str):

        return self._service.get(
            f'units/{unit_id}',
            response_schema=UnitGetResponse
        )

    def create(self, unit_body: UnitPostBody):

        return self._service.post(
            f'units',
            headers={'Content-type': 'application/json'},
            data=unit_body.json(by_alias=True),
            response_schema=UnitGetResponse
        )

    def update(self, unit_id: UUID, unit_body: UnitPatchBody):

        return self._service.patch(
            f'units/{str(unit_id)}',
            headers={'Content-type': 'application/json'},
            data=unit_body.json(exclude_unset=True, by_alias=True),
            response_schema=UnitGetResponse
        )

    def delete(self, unit_id: UUID):

        return self._service.delete(
            f'units/{str(unit_id)}'
        )
