from typing import Optional, TypeVar, Any
from uuid import UUID
from pydantic import BaseModel, PrivateAttr, ConfigDict, computed_field
from pydantic.alias_generators import to_camel

T = TypeVar("T", bound=BaseModel)


class HydroServerResourceModel(BaseModel):
    _uid: Optional[UUID] = PrivateAttr()
    _model_ref: str = PrivateAttr()
    _original_data: Optional[dict] = PrivateAttr()

    def __init__(self, _connection, _model_ref, _uid: Optional[UUID] = None, **data):
        super().__init__(**data)

        self._uid = UUID(_uid) if isinstance(_uid, str) else _uid
        self._connection = _connection
        self._model_ref = _model_ref
        self._original_data = self.dict(by_alias=False).copy()

    @computed_field
    @property
    def uid(self) -> Optional[UUID]:
        """The unique identifier for this resource."""

        return self._uid

    @property
    def _patch_data(self) -> dict:
        return {
            key: getattr(self, key)
            for key, value in self._original_data.items()
            if hasattr(self, key) and getattr(self, key) != value
        }

    def _refresh(self) -> None:
        """Refresh this resource from HydroServer."""

        self._original_data = (
            getattr(self._connection, self._model_ref)
            .get(uid=self.uid)
            .model_dump(exclude=["uid"])
        )
        self.__dict__.update(self._original_data)

    def _save(self) -> None:
        if self._patch_data:
            entity = getattr(self._connection, self._model_ref).update(
                uid=self.uid, **self._patch_data
            )
            self._original_data = entity.dict(by_alias=False, exclude=["uid"])
            self.__dict__.update(self._original_data)

    def _delete(self) -> None:
        if not self._uid:
            raise AttributeError("This resource cannot be deleted: UID is not set.")

        getattr(self._connection, self._model_ref).delete(uid=self._uid)
        self._uid = None

    model_config = ConfigDict(
        validate_assignment=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        alias_generator=to_camel,
    )


class HydroServerCollectionModel(BaseModel):
    _model_ref: str = PrivateAttr()

    filters: Optional[dict[str, Any]] = None
    ordering: Optional[list[str]] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_count: Optional[int] = None

    def __init__(self, _connection, _model_ref, _uid: Optional[UUID] = None, **data):
        super().__init__(**data)

        self._connection = _connection
        self._model_ref = _model_ref

    def next_page(self):
        """Fetches the next page of data from HydroServer."""

        return getattr(self._connection, self._model_ref).list(params=self.filters, pagination={
            "page": self.page + 1, "page_size": self.page_size, "ordering": self.ordering
        })

    def previous_page(self):
        """Fetches the previous page of data from HydroServer."""

        if self.page <= 1:
            return None

        return getattr(self._connection, self._model_ref).list(params=self.filters, pagination={
            "page": self.page - 1, "page_size": self.page_size, "ordering": self.ordering
        })
