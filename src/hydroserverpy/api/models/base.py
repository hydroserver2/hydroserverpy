from typing import Optional
from uuid import UUID
from pydantic import BaseModel, PrivateAttr, ConfigDict, computed_field
from pydantic.alias_generators import to_camel


class HydroServerBaseModel(BaseModel):
    _uid: Optional[UUID] = PrivateAttr()

    def __init__(self, _uid: Optional[UUID] = None, **data):
        super().__init__(**data)
        self._uid = _uid

    @computed_field
    @property
    def uid(self) -> Optional[UUID]:
        """The unique identifier for this resource."""

        return self._uid

    model_config = ConfigDict(
        validate_assignment=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        alias_generator=to_camel,
    )


class HydroServerModel(HydroServerBaseModel):
    _model_ref: str = PrivateAttr()
    _original_data: Optional[dict] = PrivateAttr()

    def __init__(self, _connection, _model_ref, _uid: Optional[UUID] = None, **data):
        if isinstance(_uid, str):
            _uid = UUID(_uid)

        super().__init__(_uid=_uid, **data)

        self._connection = _connection
        self._model_ref = _model_ref
        self._original_data = self.dict(by_alias=False).copy()

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
