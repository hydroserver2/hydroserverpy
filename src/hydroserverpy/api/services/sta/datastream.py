import json
import pandas as pd
from typing import Union, Optional, Literal, List, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from hydroserverpy.api.models import Datastream, DatastreamCollection
from ..base import EndpointService

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


class DatastreamService(EndpointService):
    def __init__(self, connection: "HydroServer"):
        self._model = Datastream
        self._collection_model = DatastreamCollection
        self._api_route = "api/data"
        self._endpoint_route = "datastreams"
        self._sta_route = "api/sensorthings/v1.1/Datastreams"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
        thing: Optional[Union["Thing", UUID, str]] = None,
        sensor: Optional[Union["Sensor", UUID, str]] = None,
        observed_property: Optional[Union["ObservedProperty", UUID, str]] = None,
        processing_level: Optional[Union["ProcessingLevel", UUID, str]] = None,
        unit: Optional[Union["Unit", UUID, str]] = None,
        observation_type: Optional[str] = None,
        sampled_medium: Optional[str] = None,
        status: Optional[str] = None,
        result_type: Optional[str] = None,
        is_private: Optional[bool] = None,
        value_count_max: Optional[int] = None,
        value_count_min: Optional[int] = None,
        phenomenon_begin_time_max: Optional[datetime] = None,
        phenomenon_begin_time_min: Optional[datetime] = None,
        phenomenon_end_time_max: Optional[datetime] = None,
        phenomenon_end_time_min: Optional[datetime] = None,
        result_begin_time_max: Optional[datetime] = None,
        result_begin_time_min: Optional[datetime] = None,
        result_end_time_max: Optional[datetime] = None,
        result_end_time_min: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[List[str]] = None,
    ) -> List["Datastream"]:
        """Fetch a collection of datastreams."""

        params = {}

        if workspace is not None:
            params["workspace"] = str(getattr(workspace, "uid", workspace))
        if thing is not None:
            params["thing"] = str(getattr(thing, "uid", thing))
        if sensor is not None:
            params["sensor"] = str(getattr(sensor, "uid", sensor))
        if observed_property is not None:
            params["observed_property"] = str(getattr(observed_property, "uid", observed_property))
        if processing_level is not None:
            params["processing_level"] = str(getattr(processing_level, "uid", processing_level))
        if unit is not None:
            params["unit"] = str(getattr(unit, "uid", unit))
        if observation_type is not None:
            params["observation_type"] = observation_type
        if sampled_medium is not None:
            params["sampled_medium"] = sampled_medium
        if status is not None:
            params["status"] = status
        if result_type is not None:
            params["result_type"] = result_type
        if is_private is not None:
            params["is_private"] = is_private
        if value_count_max is not None:
            params["value_count_max"] = value_count_max
        if value_count_min is not None:
            params["value_count_min"] = value_count_min
        if phenomenon_begin_time_max is not None:
            params["phenomenon_begin_time_max"] = phenomenon_begin_time_max
        if phenomenon_begin_time_min is not None:
            params["phenomenon_begin_time_min"] = phenomenon_begin_time_min
        if phenomenon_end_time_max is not None:
            params["phenomenon_end_time_max"] = phenomenon_end_time_max
        if phenomenon_end_time_min is not None:
            params["phenomenon_end_time_min"] = phenomenon_end_time_min
        if result_begin_time_max is not None:
            params["result_begin_time_max"] = result_begin_time_max
        if result_begin_time_min is not None:
            params["result_begin_time_min"] = result_begin_time_min
        if result_end_time_max is not None:
            params["result_end_time_max"] = result_end_time_max
        if result_end_time_min is not None:
            params["result_end_time_min"] = result_end_time_min

        pagination = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
        }

        return super()._list(params=params, pagination=pagination)

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
