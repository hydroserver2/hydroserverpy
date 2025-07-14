from typing import TYPE_CHECKING, Type, Union, Optional
from datetime import datetime
from uuid import UUID

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models.base import HydroServerResourceModel, HydroServerCollectionModel


class EndpointService:
    _model: Type["HydroServerResourceModel"]
    _collection_model: Type["HydroServerCollectionModel"]
    _api_route: str
    _endpoint_route: str

    def __init__(self, connection: "HydroServer") -> None:
        self._connection = connection

    def _list(self, params: Optional[dict] = None, pagination: Optional[dict] = None):
        path = f"/{self._api_route}/{self._endpoint_route}"

        if pagination is not None:
            params["page"] = pagination.get("page", 1)
            params["page_size"] = pagination.get("page_size", 100)
            if pagination.get("order_by") is not None:
                params["order_by"] = ",".join(pagination["order_by"])

        response = self._connection.request("get", path, params=params)

        return self._collection_model(
            _connection=self._connection,
            data=[
                self._model(
                    _connection=self._connection, _uid=UUID(str(obj.pop("id"))), **obj
                )
                for obj in response.json()
            ],
            filters={
                k: v for k, v in params.items() if k not in ["page", "page_size", "order_by"]
            } or None,
            order_by=pagination.get("order_by"),
            page=response.headers.get("X-Page"),
            page_size=response.headers.get("X-Page-Size"),
            total_count=response.headers.get("X-Total-Count"),
        )

    def _get(self, uid: Union[UUID, str]):
        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}"
        response = self._connection.request("get", path).json()

        return self._model(
            _connection=self._connection, _uid=UUID(str(response.pop("id"))), **response
        )

    def _create(self, **kwargs):
        path = f"/{self._api_route}/{self._endpoint_route}"
        headers = {"Content-type": "application/json"}
        response = self._connection.request(
            "post", path, headers=headers, json=self._to_iso_time(kwargs)
        ).json()

        return self._model(
            _connection=self._connection, _uid=UUID(str(response.pop("id"))), **response
        )

    def _update(self, uid: Union[UUID, str], **kwargs):
        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}"
        headers = {"Content-type": "application/json"}
        response = self._connection.request(
            "patch", path, headers=headers, json=self._to_iso_time(kwargs)
        ).json()

        return self._model(
            _connection=self._connection, _uid=UUID(str(response.pop("id"))), **response
        )

    def _delete(self, uid: Union[UUID, str]):
        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}"
        response = self._connection.request("delete", path)

        return response

    def _to_iso_time(self, obj):
        if isinstance(obj, dict):
            return {k: self._to_iso_time(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._to_iso_time(i) for i in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return obj


class SensorThingsService(EndpointService):
    _sta_route: str

    def __init__(self, connection) -> None:
        super().__init__(connection)

    def _list(self, path: Optional[str] = None, params: Optional[dict] = None):
        path = path or f"/{self._sta_route}"
        response = self._connection.request("get", path, params=params)

        return [
            self._model(_connection=self._connection, _uid=obj.pop("@iot.id"), **obj)
            for obj in response.json()["value"]
        ]

    def _get(
        self,
        uid: Union[UUID, str],
        path: Optional[str] = None,
        params: Optional[dict] = None,
    ):
        path = path or f"/{self._sta_route}('{str(uid)}')"
        response = self._connection.request("get", path, params=params).json()

        return self._model(
            _connection=self._connection, _uid=response.pop("@iot.id"), **response
        )
