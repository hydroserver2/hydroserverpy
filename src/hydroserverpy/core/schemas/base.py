from pydantic import BaseModel, PrivateAttr, AliasGenerator, AliasChoices, computed_field
from pydantic.alias_generators import to_camel
from uuid import UUID
from typing import Optional


base_alias_generator = AliasGenerator(
    serialization_alias=lambda field_name: to_camel(field_name),
    validation_alias=lambda field_name: AliasChoices(to_camel(field_name), field_name),
)


class HydroServerBaseModel(BaseModel):
    """
    A base model for HydroServer entities that provides common attributes and functionality for HydroServer data.

    :ivar _uid: A private attribute for storing the unique identifier (UUID) of the model.
    """

    _uid: Optional[UUID] = PrivateAttr()

    def __init__(self, _uid: Optional[UUID] = None, **data):
        """
        Initialize a HydroServerBaseModel instance.

        :param _uid: The unique identifier for the model.
        :type _uid: Optional[UUID]
        :param data: Additional attributes for the model.
        """

        super().__init__(**data)
        self._uid = _uid

    @computed_field
    @property
    def uid(self) -> Optional[UUID]:
        """
        The unique identifier (UUID) of the model.

        :return: The UUID of the model.
        :rtype: Optional[UUID]
        """

        return self._uid

    class Config:
        alias_generator = base_alias_generator
        validate_assignment = True


class HydroServerCoreModel(HydroServerBaseModel):
    """
    A core model for HydroServer entities that includes methods for data manipulation and persistence.

    :ivar _original_data: A private attribute storing the original data used to initialize the model.
    """

    _original_data: Optional[dict] = PrivateAttr()

    def __init__(self, _endpoint, _uid: Optional[UUID] = None, **data):
        """
        Initialize a HydroServerCoreModel instance.

        :param _endpoint: The endpoint associated with the model.
        :param _uid: The unique identifier for the model.
        :type _uid: Optional[UUID]
        :param data: Additional attributes for the model.
        """

        super().__init__(_uid=_uid, **data)
        self._endpoint = _endpoint
        self._original_data = self.dict(by_alias=False).copy()

    @property
    def _patch_data(self) -> dict:
        """
        Generate a dictionary of modified data that needs to be patched on the server.

        :return: A dictionary of modified attributes.
        :rtype: dict
        """

        return {
            key: getattr(self, key) for key, value in self._original_data.items()
            if hasattr(self, key) and getattr(self, key) != value
        }

    def refresh(self) -> None:
        """
        Refresh the model with the latest data from the server.
        """

        entity = self._endpoint.get(uid=self.uid).model_dump(exclude=['uid'])
        self._original_data = entity.dict(by_alias=False, exclude=['uid'])
        self.__dict__.update(self._original_data)

    def save(self) -> None:
        """
        Save the current state of the model to the server by updating modified attributes.
        """

        if self._patch_data:
            entity = self._endpoint.update(uid=self.uid, **self._patch_data)
            self._original_data = entity.dict(by_alias=False, exclude=['uid'])
            self.__dict__.update(self._original_data)

    def delete(self) -> None:
        """
        Delete the model from the server.

        :raises AttributeError: If the model's UID is not set.
        """

        if not self._uid:
            raise AttributeError('This resource cannot be deleted: UID is not set.')
        self._endpoint.delete(uid=self._uid)
        self._uid = None
