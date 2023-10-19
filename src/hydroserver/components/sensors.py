class Sensor:

    def __init__(self, service):
        self._service = service

    def list(self):
        pass

    def get(self, sensor_id: str):

        return self._service.get(f'sensors/{sensor_id}')
