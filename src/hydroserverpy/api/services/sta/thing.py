import json
from typing import TYPE_CHECKING, Union, IO, List, Dict, Optional, Tuple
from uuid import UUID
from ..base import EndpointService
from hydroserverpy.api.models import Thing


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class ThingService(EndpointService):
    def __init__(self, connection: "HydroServer"):
        self._model = Thing
        self._api_route = "api/data"
        self._endpoint_route = "things"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
        bbox: Optional[List[Tuple[float, float, float, float]]] = None,
        state: Optional[List[str]] = None,
        county: Optional[List[str]] = None,
        country: Optional[List[str]] = None,
        site_type: Optional[List[str]] = None,
        sampling_feature_type: Optional[List[str]] = None,
        sampling_feature_code: Optional[List[str]] = None,
        tag: Optional[List[Tuple[str, str]]] = None,
        is_private: Optional[bool] = None,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[List[str]] = None,
    ) -> List["Thing"]:
        """Fetch a collection of things."""

        params = {}

        if workspace is not None:
            params["workspace"] = [str(getattr(i, 'uid', i)) for i in workspace]
        if bbox is not None:
            params["bbox"] = [",".join([str(c) for c in i]) for i in bbox]
        if state is not None:
            params["state"] = state
        if county is not None:
            params["county"] = county
        if country is not None:
            params["country"] = country
        if site_type is not None:
            params["site_type"] = site_type
        if sampling_feature_type is not None:
            params["sampling_feature_type"] = sampling_feature_type
        if sampling_feature_code is not None:
            params["sampling_feature_code"] = sampling_feature_code
        if tag is not None:
            params["tag"] = [f"{str(i[0])}:{str(i[1])}" for i in tag]
        if is_private is not None:
            params["is_private"] = is_private

        pagination = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
        }

        return super()._list(params=params, pagination=pagination)

    def get(
        self, uid: Union[UUID, str]
    ) -> "Thing":
        """Get a thing by ID."""

        return self._get(
            uid=str(uid),
        )

    def create(
        self,
        workspace: Union["Workspace", UUID, str],
        name: str,
        description: str,
        sampling_feature_type: str,
        sampling_feature_code: str,
        site_type: str,
        is_private: False,
        latitude: float,
        longitude: float,
        elevation_m: Optional[float] = None,
        elevation_datum: Optional[str] = None,
        state: Optional[str] = None,
        county: Optional[str] = None,
        country: Optional[str] = None,
        data_disclaimer: Optional[str] = None,
    ) -> "Thing":
        """Create a new thing."""

        kwargs = {
            "name": name,
            "description": description,
            "samplingFeatureType": sampling_feature_type,
            "samplingFeatureCode": sampling_feature_code,
            "siteType": site_type,
            "isPrivate": is_private,
            "latitude": latitude,
            "longitude": longitude,
            "elevation_m": elevation_m,
            "elevationDatum": elevation_datum,
            "state": state,
            "county": county,
            "country": country,
            "dataDisclaimer": data_disclaimer,
            "workspaceId": str(getattr(workspace, "uid", workspace)),
        }

        return super()._create(**kwargs)

    def update(
        self,
        uid: Union[UUID, str],
        name: str = ...,
        description: str = ...,
        sampling_feature_type: str = ...,
        sampling_feature_code: str = ...,
        site_type: str = ...,
        is_private: False = ...,
        latitude: float = ...,
        longitude: float = ...,
        elevation_m: Optional[float] = ...,
        elevation_datum: Optional[str] = ...,
        state: Optional[str] = ...,
        county: Optional[str] = ...,
        country: Optional[str] = ...,
        data_disclaimer: Optional[str] = ...,
    ) -> "Thing":
        """Update a thing."""

        kwargs = {
            "name": name,
            "description": description,
            "samplingFeatureType": sampling_feature_type,
            "samplingFeatureCode": sampling_feature_code,
            "siteType": site_type,
            "isPrivate": is_private,
            "latitude": latitude,
            "longitude": longitude,
            "elevation_m": elevation_m,
            "elevationDatum": elevation_datum,
            "state": state,
            "county": county,
            "country": country,
            "dataDisclaimer": data_disclaimer,
        }

        return super()._update(
            uid=str(uid), **{k: v for k, v in kwargs.items() if v is not ...}
        )

    def delete(self, uid: Union[UUID, str]) -> None:
        """Delete a thing."""

        super()._delete(uid=str(uid))

    def add_tag(self, uid: Union[UUID, str], key: str, value: str) -> Dict[str, str]:
        """Tag a HydroServer thing."""

        return self._connection.request(
            "post",
            f"{self._api_route}/{self._endpoint_route}/{str(uid)}/tags",
            data=json.dumps({"key": key, "value": value}),
        ).json()

    def update_tag(self, uid: Union[UUID, str], key: str, value: str) -> Dict[str, str]:
        """Update the tag of a HydroServer thing."""

        return self._connection.request(
            "put",
            f"{self._api_route}/{self._endpoint_route}/{str(uid)}/tags",
            data=json.dumps({"key": key, "value": value}),
        ).json()

    def delete_tag(self, uid: Union[UUID, str], key: str) -> None:
        """Remove a tag from a HydroServer thing."""

        self._connection.request(
            "delete",
            f"{self._api_route}/{self._endpoint_route}/{str(uid)}/tags",
            data=json.dumps({"key": key}),
        )

    def add_photo(self, uid: Union[UUID, str], file: IO[bytes]) -> Dict[str, str]:
        """Add a photo of a HydroServer thing."""

        return self._connection.request(
            "post",
            f"{self._api_route}/{self._endpoint_route}/{str(uid)}/photos",
            files={"file": file},
        ).json()

    def delete_photo(self, uid: Union[UUID, str], name: str) -> None:
        """Delete a photo of a HydroServer thing."""

        self._connection.request(
            "delete",
            f"{self._api_route}/{self._endpoint_route}/{str(uid)}/photos",
            data=json.dumps({"name": name}),
        )
