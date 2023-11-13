import inspect
from pydantic import BaseModel
from typing import Callable


def allow_partial(*fields) -> Callable:
    """
    The allow_partial function is a decorator that allows you to mark fields as not required.
    This means that the field will be allowed to be missing from the input data, and if it is missing,
    the default value for the field will be used instead. This can also be done by setting required=False on each field.

    :return: A decorator that can be applied to a class
    """

    def dec(_cls):
        for field in fields:
            _cls.__fields__[field].required = False
        return _cls

    if fields and inspect.isclass(fields[0]) and issubclass(fields[0], BaseModel):
        cls = fields[0]
        fields = cls.__fields__
        return dec(cls)

    return dec


def entity_path(self, entity_id):
    """
    The entity_path function returns the path to a specific entity.

    :param self: Represent the instance of the class
    :param entity_id: Specify the entity id of the entity to be retrieved
    :return: The entity type and the id of the entity
    """

    return "{}({})".format(self.entitytype_plural, entity_id)
