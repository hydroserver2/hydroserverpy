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
    def __init__(self, extractor, transformer, loader, filter_out_old_data=True):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader
        self.filter_out_old_data = filter_out_old_data

    def run(self):
        """
        Extracts and transforms data as defined by the class parameters and
        loads them into a HydroServer database instance.

        :param self
        :return: None
        """

        # TODO: This implementation assumes the loader is a HydroServer core class instance
        # with a datastreams property. Probably we want to generalize this so people can create
        # their own loaders with the following methods:
        #   loader.get_end_times(): gets the timestamp of the last observation for each target timeseries
        #                           so we know the timeframe for extract and or loading
        #   loader.load(): pass in standard DataFrame, filter out old data, & post to target system
        if (
            self.filter_out_old_data
            or self.extractor.needs_datastreams
            or (self.transformer and self.transformer.needs_datastreams)
        ):
            # TODO: instead of fetching all the datastreams and filtering, just get the ones we need.
            datastreams = self.loader.datastreams.list(owned_only=True)
            if not datastreams:
                logging.error("No datastreams fetched. ETL process aborted.")
                raise "No datastreams fetched. ETL process aborted."
            ds_ids = set(self.transformer.datastream_ids.values())
            filtered_datastreams = [ds for ds in datastreams if str(ds.uid) in ds_ids]
            datastreams = {str(ds.uid): ds for ds in filtered_datastreams}

        # Step 1: Extract data
        if self.extractor.needs_datastreams:
            data = self.extractor.extract(datastreams=datastreams)
        else:
            data = self.extractor.extract()

        # TODO: Since the returned payload for each extractor will be different, we may want to have
        # an extractor property that determines if no payload was returned.
        if data is None:
            logging.warning(f"No data was returned from the extractor.")
            return
        else:
            logging.info(f"Successfully extracted data.")

        # Step 2: Transform data
        if self.transformer:
            if self.transformer.needs_datastreams:
                data = self.transformer.transform(data, datastreams)
            else:
                data = self.transformer.transform(data)

            if data is None or (isinstance(data, pd.DataFrame) and data.empty):
                logging.warning(f"No data was returned from the transformer.")
                return
            else:
                logging.info(f"Successfully transformed data.")

        # At this point, data will be a standardized Pandas dataframe in the following format:
        # pd.Timestamp    datastream_id_1(UUID)   datastream_id_2(UUID)

        # Step 3: Process and load each column individually
        for ds_id in data.columns:
            if ds_id == "timestamp":
                continue

            df = data[["timestamp", ds_id]].copy()
            df.rename(columns={ds_id: "value"}, inplace=True)
            df.dropna(subset=["value"], inplace=True)

            if self.filter_out_old_data:
                datastream = datastreams.get(ds_id)
                phenomenon_end_time = datastream.phenomenon_end_time
                if phenomenon_end_time:
                    end_time = pd.to_datetime(phenomenon_end_time)
                    df = df[df["timestamp"] > end_time]

            self.loader.datastreams.load_observations(uid=ds_id, observations=df)
