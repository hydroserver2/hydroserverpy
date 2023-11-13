from typing import List
from uuid import UUID
from hydroserverpy.schemas.sensors import SensorGetResponse, SensorPostBody, \
     SensorPatchBody


class Sensor:

    def __init__(self, service):
        self._service = service

    def list(self):

        return self._service.get(
            'sensors',
            response_schema=List[SensorGetResponse]
        )

    def get(self, sensor_id: str):

        return self._service.get(
            f'sensors/{sensor_id}',
            response_schema=SensorGetResponse
        )

    def create(self, sensor_body: SensorPostBody):

        return self._service.post(
            f'sensors',
            headers={'Content-type': 'application/json'},
            data=sensor_body.json(by_alias=True),
            response_schema=SensorGetResponse
        )

    def update(self, sensor_id: UUID, sensor_body: SensorPatchBody):

        return self._service.patch(
            f'sensors/{str(sensor_id)}',
            headers={'Content-type': 'application/json'},
            data=sensor_body.json(exclude_unset=True, by_alias=True),
            response_schema=SensorGetResponse
        )

    def delete(self, sensor_id: UUID):

        return self._service.delete(
            f'sensors/{str(sensor_id)}'
        )
