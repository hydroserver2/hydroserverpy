from typing import List
from uuid import UUID
from hydroserverpy.schemas.observed_properties import ObservedPropertyGetResponse, ObservedPropertyPostBody, \
     ObservedPropertyPatchBody


class ObservedProperty:

    def __init__(self, service):
        self._service = service

    def list(self):

        return self._service.get(
            'observed-properties',
            response_schema=List[ObservedPropertyGetResponse]
        )

    def get(self, observed_property_id: UUID):

        return self._service.get(
            f'observed-properties/{observed_property_id}',
            response_schema=ObservedPropertyGetResponse
        )

    def create(self, observed_property_body: ObservedPropertyPostBody):

        return self._service.post(
            f'observed-properties',
            headers={'Content-type': 'application/json'},
            data=observed_property_body.json(by_alias=True),
            response_schema=ObservedPropertyGetResponse
        )

    def update(self, observed_property_id: UUID, observed_property_body: ObservedPropertyPatchBody):

        return self._service.patch(
            f'observed-properties/{str(observed_property_id)}',
            headers={'Content-type': 'application/json'},
            data=observed_property_body.json(exclude_unset=True, by_alias=True),
            response_schema=ObservedPropertyGetResponse
        )

    def delete(self, observed_property_id: UUID):

        return self._service.delete(
            f'observed-properties/{str(observed_property_id)}'
        )
