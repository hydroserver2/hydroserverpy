import logging
import pandas as pd


"""
TODO: Validate input data_source file -
        Validate each datastream_id has a live datastream.
        Validate the number of datastream_ids match the number of measurement types.
TODO: An admin may delete a datastream, but still have it listed in the orchestrator.
        This shouldn't bring down the entire system so we should skip ETL for missing
        datastreams & report an error.
"""


class HydroServerETL:
    def __init__(self, extractor, transformer, loader, source_target_map):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader
        self.source_target_map = source_target_map

    def run(self):
        """
        Extracts and transforms data as defined by the class parameters and
        loads them into a HydroServer database instance.

        :param self
        :return: None
        """

        # Step 1: Get Target System data requirements from the Loader & prepare parameters for the Extractor
        data_requirements = self.loader.get_data_requirements(self.source_target_map)
        self.extractor.prepare_params(data_requirements)

        # Step 2: Extract
        data = self.extractor.extract()
        if data is None or (isinstance(data, pd.DataFrame) and data.empty):
            logging.warning(f"No data was returned from the extractor. Ending ETL run.")
            return
        else:
            logging.info(f"Successfully extracted data.")

        # Step 3: Transform
        if self.transformer:
            data = self.transformer.transform(data)
            if data is None or (isinstance(data, pd.DataFrame) and data.empty):
                logging.warning(f"No data returned from the transformer. Ending run.")
                return
            else:
                logging.info(f"Successfully transformed data. {data}")

        # Step 4: Load
        self.loader.load(data, self.source_target_map)
        logging.info("Successfully loaded data.")
