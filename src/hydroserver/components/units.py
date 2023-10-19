class Unit:

    def __init__(self, service):
        self._service = service

    def list(self):
        pass

    def get(self, unit_id: str):

        return self._service.get(f'units/{unit_id}')
