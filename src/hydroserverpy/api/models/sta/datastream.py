from typing import Union, Optional, Literal, TYPE_CHECKING
from pydantic import BaseModel, Field, AliasChoices, AliasPath, field_validator
from pandas import DataFrame
from uuid import UUID
from datetime import datetime
from ..base import HydroServerModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import (
        Workspace,
        Thing,
        Sensor,
        ObservedProperty,
        Unit,
        ProcessingLevel,
    )


class DatastreamFields(BaseModel):
    name: str = Field(..., max_length=255)
    description: str
    observation_type: str = Field(..., max_length=255)
    sampled_medium: str = Field(
        ...,
        max_length=255,
        validation_alias=AliasChoices(
            "sampledMedium", AliasPath("properties", "sampledMedium")
        ),
    )
    no_data_value: float = Field(
        ...,
        validation_alias=AliasChoices(
            "noDataValue", AliasPath("properties", "noDataValue")
        ),
    )
    aggregation_statistic: str = Field(
        ...,
        max_length=255,
        validation_alias=AliasChoices(
            "aggregationStatistic", AliasPath("properties", "aggregationStatistic")
        ),
    )
    time_aggregation_interval: float = Field(
        ...,
        validation_alias=AliasChoices(
            "timeAggregationInterval",
            AliasPath("properties", "timeAggregationInterval"),
        ),
    )
    status: Optional[str] = Field(
        None,
        max_length=255,
        validation_alias=AliasChoices("status", AliasPath("properties", "status")),
    )
    result_type: str = Field(
        ...,
        max_length=255,
        validation_alias=AliasChoices(
            "resultType", AliasPath("properties", "resultType")
        ),
    )
    value_count: Optional[int] = Field(
        None,
        ge=0,
        validation_alias=AliasChoices(
            "valueCount", AliasPath("properties", "valueCount")
        ),
    )
    phenomenon_begin_time: Optional[datetime] = Field(
        None, validation_alias=AliasChoices("phenomenonBeginTime", "phenomenonTime")
    )
    phenomenon_end_time: Optional[datetime] = Field(
        None, validation_alias=AliasChoices("phenomenonEndTime", "phenomenonTime")
    )
    result_begin_time: Optional[datetime] = Field(
        None, validation_alias=AliasChoices("resultBeginTime", "resultTime")
    )
    result_end_time: Optional[datetime] = Field(
        None, validation_alias=AliasChoices("resultEndTime", "resultTime")
    )
    is_private: bool = Field(
        False,
        validation_alias=AliasChoices(
            "isPrivate", AliasPath("properties", "isPrivate")
        ),
    )
    is_visible: bool = Field(
        True,
        validation_alias=AliasChoices(
            "isVisible", AliasPath("properties", "isVisible")
        ),
    )
    time_aggregation_interval_unit: Literal["seconds", "minutes", "hours", "days"] = (
        Field(
            ...,
            validation_alias=AliasChoices(
                "timeAggregationIntervalUnit",
                AliasPath("properties", "timeAggregationIntervalUnitOfMeasurement"),
            ),
        )
    )
    intended_time_spacing: Optional[float] = Field(
        None,
        validation_alias=AliasChoices(
            "intendedTimeSpacing", AliasPath("properties", "intendedTimeSpacing")
        ),
    )
    intended_time_spacing_unit: Optional[
        Literal["seconds", "minutes", "hours", "days"]
    ] = Field(
        None,
        validation_alias=AliasChoices(
            "intendedTimeSpacingUnit",
            AliasPath("properties", "intendedTimeSpacingUnit"),
        ),
    )

    @field_validator(
        "phenomenon_begin_time",
        "phenomenon_end_time",
        "result_begin_time",
        "result_end_time",
        mode="before",
    )
    def split_time(cls, value: str, info) -> str:
        if isinstance(value, str):
            parts = value.split("/")
            return parts[0] if "begin" in info.field_name else parts[-1]
        return value


class Datastream(HydroServerModel, DatastreamFields):
    def __init__(
        self,
        _connection: "HydroServer",
        _uid: Union[UUID, str],
        **data,
    ):
        super().__init__(
            _connection=_connection, _model_ref="datastreams", _uid=_uid, **data
        )

        self._workspace = None
        self._thing = None
        self._observed_property = None
        self._unit = None
        self._processing_level = None
        self._sensor = None

    @property
    def workspace(self) -> "Workspace":
        """The workspace this datastream belongs to."""

        if self._workspace is None:
            datastream = self._connection.request("get", f"/api/data/datastreams/{str(self.uid)}").json()
            self._workspace = self._connection.workspaces.get(uid=datastream["workspaceId"])

        return self._workspace

    @property
    def thing(self) -> "Thing":
        """The thing this datastream belongs to."""

        if self._thing is None:
            self._thing = self._connection.things.get(
                uid=self.uid,
                fetch_by_datastream_uid=True,
            )
            self._original_data["thing"] = self._thing

        return self._thing

    @thing.setter
    def thing(self, thing: Union["Thing", UUID, str]):
        if not thing:
            raise ValueError("Thing of datastream cannot be None.")
        if str(getattr(thing, "uid", thing)) != str(self.thing.uid):
            self._thing = self._connection.things.get(
                uid=str(getattr(thing, "uid", thing))
            )

    @property
    def sensor(self) -> "Sensor":
        """The sensor this datastream uses."""

        if self._sensor is None:
            self._sensor = self._connection.sensors.get(
                uid=self.uid,
                fetch_by_datastream_uid=True,
            )
            self._original_data["sensor"] = self._sensor

        return self._sensor

    @sensor.setter
    def sensor(self, sensor: Union["Sensor", UUID, str]):
        if not sensor:
            raise ValueError("Sensor of datastream cannot be None.")
        if str(getattr(sensor, "uid", sensor)) != str(self.sensor.uid):
            self._sensor = self._connection.sensors.get(
                uid=str(getattr(sensor, "uid", sensor))
            )

    @property
    def observed_property(self) -> "Thing":
        """The observed property of this datastream."""

        if self._observed_property is None:
            self._observed_property = self._connection.observedproperties.get(
                uid=self.uid,
                fetch_by_datastream_uid=True,
            )
            self._original_data["observed_property"] = self._observed_property

        return self._observed_property

    @observed_property.setter
    def observed_property(
        self, observed_property: Union["ObservedProperty", UUID, str]
    ):
        if not observed_property:
            raise ValueError("Observed property of datastream cannot be None.")
        if str(getattr(observed_property, "uid", observed_property)) != str(
            self.observed_property.uid
        ):
            self._observed_property = self._connection.observedproperties.get(
                uid=str(getattr(observed_property, "uid", observed_property))
            )

    @property
    def unit(self) -> "Unit":
        """The unit this datastream uses."""

        if self._unit is None:
            datastream = self._connection.request("get", f"/api/data/datastreams/{str(self.uid)}").json()
            self._unit = self._connection.units.get(uid=datastream["unitId"])
            self._original_data["unit"] = self._unit

        return self._unit

    @unit.setter
    def unit(self, unit: Union["Unit", UUID, str]):
        if not unit:
            raise ValueError("Unit of datastream cannot be None.")
        if str(getattr(unit, "uid", unit)) != str(self.unit.uid):
            self._unit = self._connection.units.get(uid=str(getattr(unit, "uid", unit)))

    @property
    def processing_level(self) -> "Thing":
        """The processing level of this datastream."""

        if self._processing_level is None:
            datastream = self._connection.request("get", f"/api/data/datastreams/{str(self.uid)}").json()
            self._processing_level = self._connection.processinglevels.get(uid=datastream["processingLevelId"])
            self._original_data["processing_level"] = self._processing_level

        return self._processing_level

    @processing_level.setter
    def processing_level(self, processing_level: Union["ProcessingLevel", UUID, str]):
        if not processing_level:
            raise ValueError("Processing level of datastream cannot be None.")
        if str(getattr(processing_level, "uid", processing_level)) != str(
            self.processing_level.uid
        ):
            self._processing_level = self._connection.processinglevels.get(
                uid=str(getattr(processing_level, "uid", processing_level))
            )

    def refresh(self):
        """Refresh this datastream from HydroServer."""

        self._workspace = None
        self._thing = None
        self._observed_property = None
        self._unit = None
        self._processing_level = None
        self._sensor = None
        super()._refresh()

    def save(self):
        """Save changes to this datastream to HydroServer."""

        super()._save()

    def delete(self):
        """Delete this datastream from HydroServer."""

        super()._delete()

    def get_observations(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
        page: int = 1,
        page_size: int = 100000,
        include_quality: bool = False,
        fetch_all: bool = False,
    ) -> DataFrame:
        """Retrieve the observations for this datastream."""

        return self._connection.datastreams.get_observations(
            uid=self.uid,
            start_time=start_time,
            end_time=end_time,
            page=page,
            page_size=page_size,
            include_quality=include_quality,
            fetch_all=fetch_all,
        )

    def load_observations(
        self,
        observations: DataFrame,
    ) -> None:
        """Load a DataFrame of observations to the datastream."""

        return self._connection.datastreams.load_observations(
            uid=self.uid,
            observations=observations,
        )

    # TODO: Find a better long-term solution for this issue.
    def sync_phenomenon_end_time(self):
        """Ensures the phenomenon_end_time field matches the actual end time of the observations."""

        response = self._connection.request(
            "get", f"/api/data/datastreams/{str(self.uid)}/observations",
            params={
                "order": "desc",
                "page": 1,
                "page_size": 1
            }
        ).json()

        if len(response["phenomenon_time"]) > 0:
            self.phenomenon_end_time = datetime.fromisoformat(response["phenomenon_time"][0])
        else:
            self.phenomenon_end_time = None

        self.save()
