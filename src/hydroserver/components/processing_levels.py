class ProcessingLevel:

    def __init__(self, service):
        self._service = service

    def list(self):
        pass

    def get(self, processing_level_id: str):

        return self._service.get(f'processing-levels/{processing_level_id}')
