class DataLoader:

    def __init__(self, service):
        self._service = service

    def list(self):
        pass

    def get(self, data_loader_id: str):

        return self._service.get(f'data-loaders/{data_loader_id}')

    def load_file_data(self, data_source_id: str):

        pass
