class Datastream:

    def __init__(self, service):
        self._service = service

    def list(self):
        pass

    def get(self, datastream_id: str):

        return self._service.get(f'datastreams/{datastream_id}')
