from typing import List
from uuid import UUID
from hydroserverpy.schemas.processing_levels import ProcessingLevelGetResponse, ProcessingLevelPostBody, \
     ProcessingLevelPatchBody


class ProcessingLevel:

    def __init__(self, service):
        self._service = service

    def list(self):

        return self._service.get(
            'processing-levels',
            response_schema=List[ProcessingLevelGetResponse]
        )

    def get(self, processing_level_id: str):

        return self._service.get(
            f'processing-levels/{processing_level_id}',
            response_schema=ProcessingLevelGetResponse
        )

    def create(self, processing_level_body: ProcessingLevelPostBody):

        return self._service.post(
            f'processing-levels',
            headers={'Content-type': 'application/json'},
            data=processing_level_body.json(by_alias=True),
            response_schema=ProcessingLevelGetResponse
        )

    def update(self, processing_level_id: UUID, processing_level_body: ProcessingLevelPatchBody):

        return self._service.patch(
            f'processing-levels/{str(processing_level_id)}',
            headers={'Content-type': 'application/json'},
            data=processing_level_body.json(exclude_unset=True, by_alias=True),
            response_schema=ProcessingLevelGetResponse
        )

    def delete(self, processing_level_id: UUID):

        return self._service.delete(
            f'processing-levels/{str(processing_level_id)}'
        )
