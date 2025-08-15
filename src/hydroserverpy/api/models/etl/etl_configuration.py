from typing import Annotated, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum

WorkflowType = Literal["ETL", "Aggregation", "Virtual", "SDL"]
CSVDelimiterType = Literal[",", "|", "\t", ";", " "]
ExtractorType = Literal["HTTP", "local"]
TransformerType = Literal["JSON", "CSV"]
LoaderType = Literal["HydroServer"]
IdentifierType = Literal["name", "index"]
RunTimeValue = Literal["jobExecutionTime", "latestObservationTimestamp"]


class FixedOffsetTimezone(str, Enum):
    UTC_MINUS_1200 = "-1200"
    UTC_MINUS_1100 = "-1100"
    UTC_MINUS_1000 = "-1000"
    UTC_MINUS_0900 = "-0900"
    UTC_MINUS_0800 = "-0800"
    UTC_MINUS_0700 = "-0700"
    UTC_MINUS_0600 = "-0600"
    UTC_MINUS_0500 = "-0500"
    UTC_MINUS_0430 = "-0430"
    UTC_MINUS_0400 = "-0400"
    UTC_MINUS_0330 = "-0330"
    UTC_MINUS_0300 = "-0300"
    UTC_MINUS_0200 = "-0200"
    UTC_MINUS_0100 = "-0100"
    UTC_PLUS_0000 = "+0000"
    UTC_PLUS_0100 = "+0100"
    UTC_PLUS_0200 = "+0200"
    UTC_PLUS_0300 = "+0300"
    UTC_PLUS_0330 = "+0330"
    UTC_PLUS_0400 = "+0400"
    UTC_PLUS_0430 = "+0430"
    UTC_PLUS_0500 = "+0500"
    UTC_PLUS_0530 = "+0530"
    UTC_PLUS_0545 = "+0545"
    UTC_PLUS_0600 = "+0600"
    UTC_PLUS_0630 = "+0630"
    UTC_PLUS_0700 = "+0700"
    UTC_PLUS_0800 = "+0800"
    UTC_PLUS_0845 = "+0845"
    UTC_PLUS_0900 = "+0900"
    UTC_PLUS_0930 = "+0930"
    UTC_PLUS_1000 = "+1000"
    UTC_PLUS_1030 = "+1030"
    UTC_PLUS_1100 = "+1100"
    UTC_PLUS_1130 = "+1130"
    UTC_PLUS_1200 = "+1200"
    UTC_PLUS_1245 = "+1245"
    UTC_PLUS_1300 = "+1300"
    UTC_PLUS_1400 = "+1400"


class TimestampFormat(str, Enum):
    ISO8601 = "ISO8601"
    naive = "naive"
    custom = "custom"


class TimezoneMode(str, Enum):
    utc = "utc"  # always UTC
    daylightSavings = "daylightSavings"  # IANA / DST-aware
    fixedOffset = "fixedOffset"  # constant offset
    embeddedOffset = "embeddedOffset"  # offset in ISO string


class Timestamp(BaseModel):
    key: Optional[str] = None
    format: TimestampFormat
    custom_format: Optional[str] = Field(None, alias="customFormat")
    timezone_mode: TimezoneMode = Field(..., alias="timezoneMode")
    timezone: Optional[Union[FixedOffsetTimezone, str]] = Field(None, alias="timezone")

    class Config:
        allow_population_by_field_name = True

    @field_validator("timezone")
    def check_timezone(cls, timezone_value, info):
        mode = info.data.get("timezone_mode")
        if mode == TimezoneMode.fixedOffset and timezone_value is None:
            raise ValueError("`timezone` must be set when timezoneMode is fixedOffset")
        return timezone_value


class PerPayloadPlaceholder(BaseModel):
    name: str
    type: Literal["perPayload"]


class RunTimePlaceholder(BaseModel):
    name: str
    type: Literal["runTime"]
    run_time_value: RunTimeValue = Field(..., alias="runTimeValue")
    timestamp: Timestamp

    class Config:
        allow_population_by_field_name = True


PlaceholderVariable = Annotated[
    Union[PerPayloadPlaceholder, RunTimePlaceholder],
    Field(discriminator="type"),
]


class BaseExtractor(BaseModel):
    type: ExtractorType
    source_uri: str = Field(..., alias="sourceUri")
    placeholder_variables: Optional[List[PlaceholderVariable]] = Field(
        default_factory=list,
        alias="placeholderVariables",
    )

    class Config:
        allow_population_by_field_name = True


class HTTPExtractor(BaseExtractor):
    type: Literal["HTTP"]


class LocalFileExtractor(BaseExtractor):
    type: Literal["local"]


ExtractorConfig = Annotated[
    Union[HTTPExtractor, LocalFileExtractor], Field(discriminator="type")
]


class BaseTransformer(BaseModel):
    type: TransformerType
    timestamp: Timestamp


class JSONTransformer(BaseTransformer):
    type: Literal["JSON"]
    jmespath: str = Field(..., alias="JMESPath")

    class Config:
        allow_population_by_field_name = True


class CSVTransformer(BaseTransformer):
    type: Literal["CSV"]
    header_row: Optional[int] = Field(..., alias="headerRow")
    data_start_row: int = Field(..., alias="dataStartRow")
    delimiter: CSVDelimiterType
    identifier_type: IdentifierType = Field(..., alias="identifierType")

    class Config:
        allow_population_by_field_name = True


TransformerConfig = Union[JSONTransformer, CSVTransformer]


class BaseLoaderConfig(BaseModel):
    type: LoaderType


class HydroServerLoaderConfig(BaseLoaderConfig):
    type: Literal["HydroServer"]


LoaderConfig = HydroServerLoaderConfig


class ExpressionDataTransformation(BaseModel):
    type: Literal["expression"]
    expression: str

    class Config:
        allow_population_by_field_name = True


class LookupTableDataTransformation(BaseModel):
    type: Literal["lookup"]
    lookup_table_id: str = Field(..., alias="lookupTableId")

    class Config:
        allow_population_by_field_name = True


DataTransformation = Union[ExpressionDataTransformation, LookupTableDataTransformation]


class MappingPath(BaseModel):
    target_identifier: Union[str, int] = Field(..., alias="targetIdentifier")
    data_transformations: List[DataTransformation] = Field(
        default_factory=list, alias="dataTransformations"
    )

    class Config:
        allow_population_by_field_name = True


class SourceTargetMapping(BaseModel):
    source_identifier: Union[str, int] = Field(..., alias="sourceIdentifier")
    paths: List[MappingPath] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True


class Payload(BaseModel):
    name: str = ""
    mappings: List[SourceTargetMapping] = Field(default_factory=list)
    extractor_variables: Dict[str, str] = Field(
        default_factory=dict, alias="extractorVariables"
    )

    class Config:
        allow_population_by_field_name = True


class EtlConfiguration(BaseModel):
    type: WorkflowType
    extractor: ExtractorConfig
    transformer: TransformerConfig
    loader: LoaderConfig
    payloads: List[Payload]
