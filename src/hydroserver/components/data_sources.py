class DataSource:

    def __init__(self, service):
        self._service = service

    def list(self):
        pass

    def get(self, data_source_id: str):

        return self._service.get(f'data-sources/{data_source_id}')

    def load_file_data(self, data_source_id: str):

        pass
