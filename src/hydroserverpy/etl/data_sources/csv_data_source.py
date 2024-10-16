from ..extractors.ftp_extractor import FTPExtractor
from ..transformers.csv_transformer import CSVTransformer
from ..protocols.tcp_protocols import TCP_PROTOCOLS


class CSVDataSource:
    def __init__(self, host, port, authentication=None):
        self._timestamp_column_index = None
        self._datastream_column_indexes = None
        self._datastream_start_row_indexes = {}
        self._last_loaded_timestamp = self._data_source.data_source_thru

        self.extractor = FTPExtractor(host, port, authentication)
        self.transformer = CSVTransformer()

    async def get_data(self):
        await self.extractor.connect()
        csv_file = await self.extractor.extract()
        parsed_response = self.transformer.transform(csv_file)
        return parsed_response
