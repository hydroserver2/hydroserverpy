import logging
import pandas as pd


class HydroServerETL:
    def __init__(self, extractor, transformer, loader, source_target_map):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader
        self.source_target_map = source_target_map

    def run(self):
        """
        Extracts, transforms, and loads data as defined by the class parameters.
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
