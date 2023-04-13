import yaml
import simplejson as json
from uuid import UUID
from pydantic import BaseModel, DirectoryPath
from typing import List, Pattern, Optional


class HydroLoaderConfTimestamp(BaseModel):
    format: str = '%Y-%m-%d %H:%M:%S%z'
    column: int = 0
    utc_offset: str = '+0000'


class HydroLoaderConfDatastream(BaseModel):
    datastream: UUID
    column: int


class HydroLoaderConf(BaseModel):
    name: str
    directory: DirectoryPath
    file: Pattern
    delimiter: str = ','
    header_rows: int = 0
    footer_rows: int = 0
    timestamp: HydroLoaderConfTimestamp
    datastreams: List[HydroLoaderConfDatastream]

    def to_yaml(
            self,
            file_path: Optional[DirectoryPath] = None
    ):
        """"""

        if file_path is None:
            file_path = f'{self.name}.yaml'

        with open(file_path, 'w') as conf_file:
            yaml.dump(
                json.loads(self.json()),
                conf_file,
                sort_keys=False,
                default_flow_style=False
            )
