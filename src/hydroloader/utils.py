# import yaml
# import csv
# import simplejson as json
# from decimal import Decimal
# from pydantic import Json
# from typing import List
# from hydroloader import HydroLoaderConf
#
#
# def parse_conf(
#         conf_file
# ) -> HydroLoaderConf:
#     """"""
#
#     with open(conf_file, 'r') as yaml_file:
#         hydroloader_conf = yaml.safe_load(yaml_file)
#
#     return HydroLoaderConf(**hydroloader_conf)
#
#
# def build_observations_requests(
#         conf_file,
#         data_file,
#         observation_chunk_size: int = 1000
# ) -> List[Json]:
#     """"""
#
#     st_conf = parse_conf(conf_file)
#
#     with open(data_file, 'r') as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=st_conf.delimiter)
#         csv_columns = [
#             column[st_conf.header_rows:-st_conf.footer_rows or None]
#             for column in zip(*[map(str, row) for row in csv_reader])
#         ]
#
#     timestamps = csv_columns[st_conf.timestamp.column]
#
#     observations_data = iter([
#         item for sublist in ([
#             (str(datastream.datastream), timestamps[i], Decimal(observation))
#             for i, observation in enumerate(csv_columns[datastream.column]) if observation != ''
#         ] for datastream in st_conf.datastreams)
#         for item in sublist
#     ])
#
#     observations_chunks = []
#
#     for i, (datastream, timestamp, result) in enumerate(observations_data):
#         if i % observation_chunk_size == 0:
#             observations_chunks.append({})
#         observations_chunks[-1].setdefault(datastream, []).append([timestamp, result])
#
#     request_bodies = []
#
#     for observations_chunk in observations_chunks:
#         request_bodies.append(json.dumps([
#             {
#                 'Datastream': {
#                     '@iot.id': datastream
#                 },
#                 'components': ['resultTime', 'result'],
#                 'dataArray': observations
#             } for datastream, observations in observations_chunk.items()
#         ], use_decimal=True))
#
#     return request_bodies
