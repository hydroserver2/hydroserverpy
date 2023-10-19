class ObservedProperty:

    def __init__(self, service):
        self._service = service

    def list(self):
        pass

    def get(self, observed_property_id: str):

        return self._service.get(f'observed-properties/{observed_property_id}')
