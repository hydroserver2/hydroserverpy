from typing import List
from uuid import UUID
from hydroserverpy.schemas.result_qualifiers import ResultQualifierGetResponse, ResultQualifierPostBody, \
     ResultQualifierPatchBody


class ResultQualifier:

    def __init__(self, service):
        self._service = service

    def list(self):

        return self._service.get(
            'result-qualifiers',
            response_schema=List[ResultQualifierGetResponse]
        )

    def get(self, result_qualifier_id: str):

        return self._service.get(
            f'result-qualifiers/{result_qualifier_id}',
            response_schema=ResultQualifierGetResponse
        )
    
    def create(self, result_qualifier_body: ResultQualifierPostBody):

        return self._service.post(
            f'result-qualifiers',
            headers={'Content-type': 'application/json'},
            data=result_qualifier_body.json(by_alias=True),
            response_schema=ResultQualifierGetResponse
        )

    def update(self, result_qualifier_id: UUID, result_qualifier_body: ResultQualifierPatchBody):

        return self._service.patch(
            f'result-qualifiers/{str(result_qualifier_id)}',
            headers={'Content-type': 'application/json'},
            data=result_qualifier_body.json(exclude_unset=True, by_alias=True),
            response_schema=ResultQualifierGetResponse
        )

    def delete(self, result_qualifier_id: UUID):

        return self._service.delete(
            f'result-qualifiers/{str(result_qualifier_id)}'
        )
