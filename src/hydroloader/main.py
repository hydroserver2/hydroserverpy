import requests
from pydantic import AnyHttpUrl, Json
from typing import Tuple, List, Union


class HydroLoaderClient:
    """"""

    def __init__(
            self,
            auth: Tuple[str, str],
            service: AnyHttpUrl = 'http://127.0.0.1:8000/sensorthings/v1.1'
    ):
        self.client = requests.Session()
        self.client.auth = auth
        self.service = service

    def post_observations(
            self,
            observation_bodies: Union[List[Json], Json, List[dict], dict]
    ) -> Union[List[requests.Response], requests.Response]:
        """"""

        responses = []

        for observation_body in observation_bodies:
            responses.append(self.client.post(
                f'{self.service}/Observations',
                data=observation_body
            ))

        return responses


# print(build_observations_requests(
#     'LRO1.yaml',
#     'LRO1-1.csv',
#     2
# ))

# print(parse_conf('LRO1.yaml'))


# conf = HydroLoaderConf(
#     name='LRO1',
#     directory='/Users/klippold/Documents/',
#     file='^.*\\.(csv)$',
#     timestamp=HydroLoaderConfTimestamp(),
#     datastreams=[
#         HydroLoaderConfObservation(
#             datastream='4b12eead-1ae8-47f4-b91a-839a4007ea64',
#             column=1
#         ),
#         HydroLoaderConfObservation(
#             datastream='93fed7cc-4d23-40b3-802b-9aae1c5cf91c',
#             column=2
#         )
#     ]
# )

# conf.to_yaml()
