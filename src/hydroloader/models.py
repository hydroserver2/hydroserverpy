import yaml
import re
import simplejson as json
from uuid import UUID
from datetime import datetime
from crontab import CronTab
from pydantic import BaseModel, validator, root_validator, conint, AnyHttpUrl, Field
from typing import List, Optional, Literal, Union


class HydroLoaderDatastream(BaseModel):
    id: UUID
    value_count: Optional[int] = Field(None, alias='valueCount')
    result_time: Optional[datetime] = Field(None, alias='resultTime')
    phenomenon_time: Optional[datetime] = Field(None, alias='phenomenonTime')
    file_row_start_index: Optional[int]
    file_result_end_time: Optional[datetime]
    chunk_result_start_time: Optional[datetime]
    chunk_result_end_time: Optional[datetime]


class HydroLoaderObservationsResponse(BaseModel):
    datastream_id: str
    request_url: str
    status_code: int
    reason: str
    chunk_start_time: str
    chunk_end_time: str


class HydroLoaderConfSchedule(BaseModel):
    crontab: Optional[str]
    interval_units: Optional[Literal['minutes', 'hours', 'days', 'weeks', 'months']]
    interval: Optional[conint(gt=0)]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    paused: Optional[bool]

    @root_validator(pre=True)
    def check_crontab_or_interval(cls, values):
        """
        The check_crontab_or_interval function is a validator that ensures that the HydroLoaderConfSchedule model
        does not include both a crontab and an interval. It also ensures that if an interval is
        included, it includes both an interval and its units.

        :param cls: Pass the class of the model to be created
        :param values: Pass the values of the fields in a form to
        :return: The values dictionary
        """

        if values.get('crontab') and (values.get('interval_units') or values.get('interval')):
            raise ValueError('Schedule can include either a crontab or an interval, not both.')

        if (
            values.get('interval_units') and not values.get('interval')
        ) or (
            not values.get('interval_units') and values.get('interval')
        ):
            raise ValueError('Interval must include both an interval and interval_units.')

        return values

    @validator('crontab')
    def check_valid_crontab(cls, v):
        """
        The check_valid_crontab function is a validator that uses the CronTab library to check if the inputted
        crontab string is valid. If it's not, an exception will be raised.

        :param cls: Pass the class to the function
        :param v: Pass the value of the field to be validated
        :return: The crontab string
        """

        if v is not None:
            CronTab(v)

        return v


class HydroLoaderConfFileAccess(BaseModel):
    path: Optional[str]
    url: Optional[AnyHttpUrl]
    header_row: Optional[conint(gt=0)] = None
    data_start_row: Optional[conint(gt=0)] = 1
    delimiter: Optional[str] = ','
    quote_char: Optional[str] = '"'

    @root_validator(pre=True)
    def check_path_or_url(cls, values):
        """
        The check_path_or_url function is a validator that takes in the values of the HydroLoaderConfFileAccess model
        and checks to see if there is either a path or url. If there isn't, it raises an error.

        :param cls: Pass the class of the object being created
        :param values: Pass in the values of the path and url parameters
        :return: The values dictionary
        """

        if bool(values.get('path')) == bool(values.get('url')):
            raise ValueError('File access must include either a path or a URL.')

        return values

    @root_validator(pre=True)
    def check_header_and_data_rows(cls, values):
        """
        The check_header_and_data_rows function is a class method that takes in the values of the header_row and
        data_start_row and ensures the header row is not greater than the data start row. If it is, it raises an error.

        :param cls: Refer to the class that is being created
        :param values: Get the values of the header_row and data_start_row
        :return: The values dictionary
        """

        if values.get('header_row') is not None and values.get('header_row') >= values.get('data_start_row'):
            raise ValueError('Header row cannot occur after data start row.')

        return values

    @validator('delimiter')
    def convert_delimiters(cls, v):
        """
        The convert_delimiters function is a validator that takes in a string and replaces all instances of '\\t' with
        '\t'. This function is used to convert the delimiters from the input file into tab-delimited format.

        :param cls: Pass the class object to the function
        :param v: Pass the value of the escaped delimiter into the function
        :return: An unescaped delimiter string
        """

        return v.replace('\\t', '\t')


class HydroLoaderConfFileTimestamp(BaseModel):
    column: Union[conint(gt=0), str]
    format: Optional[str] = '%Y-%m-%dT%H:%M:%S%Z'
    offset: Optional[str] = '+0000'

    @validator('format')
    def check_valid_strftime(cls, v):
        """
        The check_valid_strftime function is a validator that takes in a datetime strf string and checks to see if it
        is valid. It uses the strftime function from the datetime module, which returns an error if the string passed
        to it is not valid.

        :param cls: Pass the class to which the validator is attached
        :param v: Pass the value of the argument to be checked
        :return: The value of the string
        """

        datetime.now().strftime(v)

        return v

    @validator('offset', always=True)
    def parse_tzinfo(cls, v):
        """
        The parse_tzinfo function is a validator for the offset field. It takes in a string and returns an instance
        of datetime.tzinfo, which is used by Python's datetime module to represent timezone information. The function
        first checks that the input string is a valid UTC offset formatted like "+0000". If it is not valid, then it
        raises an exception.

        :param cls: Pass in the class of the object being created
        :param v: Pass the timezone offset
        :return: A tzinfo object
        """

        tzinfo_pattern = r'^[+-](0[0-9]|1[0-4])[0-5][0-9]$'
        if v is not None and re.match(tzinfo_pattern, v) is None:
            raise ValueError('The offset must be a valid UTC timezone offset formatted such as "+0000".')

        return v  # datetime.strptime(v, '%z').tzinfo if v is not None else None


class HydroLoaderConfFileDatastream(BaseModel):
    column: Union[conint(gt=0), str]
    id: UUID


class HydroLoaderConf(BaseModel):
    schedule: Optional[HydroLoaderConfSchedule]
    file_access: HydroLoaderConfFileAccess
    file_timestamp: HydroLoaderConfFileTimestamp
    datastreams: List[HydroLoaderConfFileDatastream]

    @root_validator()
    def check_header_and_fields(cls, values):
        """"""

        if not values.get('file_access') or not values['file_access'].header_row:
            if values.get('file_timestamp') and not isinstance(values['file_timestamp'].column, int):
                raise ValueError('If no header row is defined, all column identifiers must be integers.')
            if values.get('datastreams'):
                for datastream in values['datastreams']:
                    if not isinstance(datastream.column, int):
                        raise ValueError('If no header row is defined, all column identifiers must be integers.')

        return values

    def to_yaml(
            self,
            file_path: str
    ):
        """
        The to_yaml function takes a file path and writes the configuration to that file in YAML format.

        :param self: Refer to the current instance of the class
        :param file_path: str: Specify the file path to save the configuration
        :return: A yaml file
        """

        with open(file_path, 'w') as conf_file:
            yaml.dump(
                json.loads(self.json()),
                conf_file,
                sort_keys=False,
                default_flow_style=False
            )
