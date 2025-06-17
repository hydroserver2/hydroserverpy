import json
import pandas as pd
from typing import Union, Optional, Literal, List, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from hydroserverpy.api.models import Datastream
from ..base import SensorThingsService


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import (
        Workspace,
        Thing,
        Unit,
        Sensor,
        ObservedProperty,
        ProcessingLevel,
    )


class DatastreamService(SensorThingsService):
    def __init__(self, connection: "HydroServer"):
        self._model = Datastream
        self._api_route = "api/data"
        self._endpoint_route = "datastreams"
        self._sta_route = "api/sensorthings/v1.1/Datastreams"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
        thing: Optional[Union["Thing", UUID, str]] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> List["Datastream"]:
        """Fetch a collection of datastreams."""

        params = {"$top": page_size, "$skip": page_size * (page - 1)}

        filters = []
        if workspace:
            filters.append(
                f"properties/workspace/id eq '{str(getattr(workspace, 'uid', workspace))}'"
            )
        if thing:
            filters.append(f"Thing/id eq '{str(getattr(thing, 'uid', thing))}'")

        if filters:
            params["$filter"] = " and ".join(filters)

        return super()._list(params=params)

    def get(self, uid: Union[UUID, str]) -> "Datastream":
        """Get a datastream by ID."""

        return super()._get(uid=str(uid))

    def create(
        self,
        name: str,
        description: str,
        thing: Union["Thing", UUID, str],
        sensor: Union["Sensor", UUID, str],
        observed_property: Union["ObservedProperty", UUID, str],
        processing_level: Union["ProcessingLevel", UUID, str],
        unit: Union["Unit", UUID, str],
        observation_type: str,
        result_type: str,
        sampled_medium: str,
        no_data_value: float,
        aggregation_statistic: str,
        time_aggregation_interval: float,
        time_aggregation_interval_unit: Literal["seconds", "minutes", "hours", "days"],
        intended_time_spacing: Optional[float] = None,
        intended_time_spacing_unit: Optional[
            Literal["seconds", "minutes", "hours", "days"]
        ] = None,
        status: Optional[str] = None,
        value_count: Optional[int] = None,
        phenomenon_begin_time: Optional[datetime] = None,
        phenomenon_end_time: Optional[datetime] = None,
        result_begin_time: Optional[datetime] = None,
        result_end_time: Optional[datetime] = None,
        is_private: bool = False,
        is_visible: bool = True,
    ) -> "Datastream":
        """Create a new datastream."""

        kwargs = {
            "name": name,
            "description": description,
            "thingId": str(getattr(thing, "uid", thing)),
            "sensorId": str(getattr(sensor, "uid", sensor)),
            "observedPropertyId": str(
                getattr(observed_property, "uid", observed_property)
            ),
            "processingLevelId": str(
                getattr(processing_level, "uid", processing_level)
            ),
            "unitId": str(getattr(unit, "uid", unit)),
            "observationType": observation_type,
            "resultType": result_type,
            "sampledMedium": sampled_medium,
            "noDataValue": no_data_value,
            "aggregationStatistic": aggregation_statistic,
            "timeAggregationInterval": time_aggregation_interval,
            "timeAggregationIntervalUnit": time_aggregation_interval_unit,
            "intendedTimeSpacing": intended_time_spacing,
            "intendedTimeSpacingUnit": intended_time_spacing_unit,
            "status": status,
            "valueCount": value_count,
            "phenomenonBeginTime": (
                phenomenon_begin_time.isoformat() if phenomenon_begin_time else None
            ),
            "phenomenonEndTime": (
                phenomenon_end_time.isoformat() if phenomenon_end_time else None
            ),
            "resultBeginTime": (
                result_begin_time.isoformat() if result_begin_time else None
            ),
            "resultEndTime": result_end_time.isoformat() if result_end_time else None,
            "isPrivate": is_private,
            "isVisible": is_visible,
        }

        return super()._create(**kwargs)

    def update(
        self,
        uid: Union[UUID, str],
        name: str = ...,
        description: str = ...,
        thing: Union["Thing", UUID, str] = ...,
        sensor: Union["Sensor", UUID, str] = ...,
        observed_property: Union["ObservedProperty", UUID, str] = ...,
        processing_level: Union["ProcessingLevel", UUID, str] = ...,
        unit: Union["Unit", UUID, str] = ...,
        observation_type: str = ...,
        result_type: str = ...,
        sampled_medium: str = ...,
        no_data_value: float = ...,
        aggregation_statistic: str = ...,
        time_aggregation_interval: float = ...,
        time_aggregation_interval_unit: Literal[
            "seconds", "minutes", "hours", "days"
        ] = ...,
        intended_time_spacing: Optional[float] = ...,
        intended_time_spacing_unit: Optional[
            Literal["seconds", "minutes", "hours", "days"]
        ] = ...,
        status: Optional[str] = ...,
        value_count: Optional[int] = ...,
        phenomenon_begin_time: Optional[datetime] = ...,
        phenomenon_end_time: Optional[datetime] = ...,
        result_begin_time: Optional[datetime] = ...,
        result_end_time: Optional[datetime] = ...,
        is_private: bool = ...,
        is_visible: bool = ...,
    ) -> "Datastream":
        """Update a datastream."""

        kwargs = {
            "name": name,
            "description": description,
            "thingId": ... if thing is ... else str(getattr(thing, "uid", thing)),
            "sensorId": ... if sensor is ... else str(getattr(sensor, "uid", sensor)),
            "observedPropertyId": (
                ...
                if observed_property is ...
                else str(getattr(observed_property, "uid", observed_property))
            ),
            "processingLevelId": (
                ...
                if processing_level is ...
                else str(getattr(processing_level, "uid", processing_level))
            ),
            "unitId": ... if unit is ... else str(getattr(unit, "uid", unit)),
            "observationType": observation_type,
            "resultType": result_type,
            "sampledMedium": sampled_medium,
            "noDataValue": no_data_value,
            "aggregationStatistic": aggregation_statistic,
            "timeAggregationInterval": time_aggregation_interval,
            "timeAggregationIntervalUnit": time_aggregation_interval_unit,
            "intendedTimeSpacing": intended_time_spacing,
            "intendedTimeSpacingUnit": intended_time_spacing_unit,
            "status": status,
            "valueCount": value_count,
            "phenomenonBeginTime": (
                phenomenon_begin_time.isoformat()
                if phenomenon_begin_time
                not in (
                    None,
                    ...,
                )
                else phenomenon_begin_time
            ),
            "phenomenonEndTime": (
                phenomenon_end_time.isoformat()
                if phenomenon_end_time
                not in (
                    None,
                    ...,
                )
                else phenomenon_end_time
            ),
            "resultBeginTime": (
                result_begin_time.isoformat()
                if result_begin_time
                not in (
                    None,
                    ...,
                )
                else result_begin_time
            ),
            "resultEndTime": (
                result_end_time.isoformat()
                if result_end_time
                not in (
                    None,
                    ...,
                )
                else result_end_time
            ),
            "isPrivate": is_private,
            "isVisible": is_visible,
        }

        return super()._update(
            uid=str(uid), **{k: v for k, v in kwargs.items() if v is not ...}
        )

    def delete(self, uid: Union[UUID, str]) -> None:
        """Delete a datastream."""

        super()._delete(uid=str(uid))

    def get_observations(
        self,
        uid: Union[UUID, str],
        start_time: datetime = None,
        end_time: datetime = None,
        page: int = 1,
        page_size: int = 100000,
        include_quality: bool = False,
        fetch_all: bool = False,
    ) -> pd.DataFrame:
        """Retrieve observations of a datastream."""

        filters = []
        if start_time:
            filters.append(
                f'phenomenonTime ge {start_time.strftime("%Y-%m-%dT%H:%M:%S%z")}'
            )
        if end_time:
            filters.append(
                f'phenomenonTime le {end_time.strftime("%Y-%m-%dT%H:%M:%S%z")}'
            )

        if fetch_all:
            page = 1

        observations = []

        while True:
            response = self._connection.request(
                "get",
                f"api/sensorthings/v1.1/Datastreams('{str(uid)}')/Observations",
                params={
                    "$resultFormat": "dataArray",
                    "$select": f'phenomenonTime,result{",resultQuality" if include_quality else ""}',
                    "$count": True,
                    "$top": page_size,
                    "$skip": (page - 1) * page_size,
                    "$filter": " and ".join(filters) if filters else None,
                },
            )
            response_content = json.loads(response.content)
            data_array = (
                response_content["value"][0]["dataArray"]
                if response_content["value"]
                else []
            )
            observations.extend(
                [
                    (
                        [
                            obs[0],
                            obs[1],
                            obs[2]["qualityCode"] if obs[2]["qualityCode"] else None,
                            (
                                obs[2]["resultQualifiers"]
                                if obs[2]["resultQualifiers"]
                                else None
                            ),
                        ]
                        if include_quality
                        else [obs[0], obs[1]]
                    )
                    for obs in data_array
                ]
            )
            if not fetch_all or len(data_array) < page_size:
                break
            page += 1

        columns = ["timestamp", "value"]
        if include_quality:
            columns.extend(["quality_code", "result_quality"])

        data_frame = pd.DataFrame(observations, columns=columns)
        data_frame["timestamp"] = pd.to_datetime(data_frame["timestamp"])

        return data_frame

    def load_observations(
        self,
        uid: Union[UUID, str],
        observations: pd.DataFrame,
    ) -> None:
        """Load observations to a datastream."""

        data_array = [
            [
                row["timestamp"].strftime("%Y-%m-%dT%H:%M:%S%z"),
                row["value"],
                (
                    {
                        "qualityCode": row.get("quality_code", None),
                        "resultQualifiers": row.get("result_qualifiers", []),
                    }
                    if "quality_code" in row or "result_qualifiers" in row
                    else {}
                ),
            ]
            for _, row in observations.iterrows()
        ]

        self._connection.request(
            "post",
            f"api/sensorthings/v1.1/CreateObservations",
            headers={"Content-type": "application/json"},
            data=json.dumps(
                [
                    {
                        "Datastream": {"@iot.id": str(uid)},
                        "components": ["phenomenonTime", "result", "resultQuality"],
                        "dataArray": data_array,
                    }
                ]
            ),
        )
