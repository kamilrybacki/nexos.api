from __future__ import annotations

import logging
from types import NoneType
from typing import Any, Self, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core._pydantic_core import PydanticUndefined, PydanticUndefinedType


class NullableBaseModel(BaseModel):
    """
    Base model that allows fields to be None.
    This is useful for cases where fields may not always have a value.
    """

    @classmethod
    def _construct_from_annotation(cls, field: FieldInfo | NullableBaseModel | type) -> Any:
        """
        Constructs a field from its annotation.
        If the field has a default value, it will be used as the return value.
        If the field type is a Union or has an origin, it will be handled accordingly,
        meaning that only the first type in the Union will be used.
        Otherwise, it will return the field name and its type as a tuple.


        :param field: The type of the field.
        :return: A tuple containing the field name and its type.
        """
        logging.info(f"Constructing {field} in class {cls.__name__}")

        if hasattr(field, "null"):
            return field.null

        field = field.annotation if isinstance(field, FieldInfo) else field  # type: ignore[assignment]

        if hasattr(field, "null"):
            return field.null

        if hasattr(field, "default") and not isinstance(field.default, (PydanticUndefinedType, PydanticUndefined)):
            return field.default

        """
        Try to call the origin if it is callable.
        This is useful for cases where the origin is a class or function
        that can be instantiated or called without arguments.

        In case of types which cannot be instantiated, we skip returning the origin
        and proceed with the next checks.
        """
        origin = get_origin(field)
        try:
            origin()  # type: ignore
        except TypeError:
            field_args = get_args(field)
            if field_args:
                if field_args[1] is NoneType:
                    return field_args[1]
                if isinstance(field_args[0], type):
                    if hasattr(field_args[0], "null"):
                        # If the first argument is a type with a null method, return that
                        return field_args[0].null

            if callable(field):
                # If the field is a callable (like a function or class), return it directly
                return field

            return field
        else:
            return origin

    @classmethod
    def _inspect_fields(cls) -> dict[str, type]:
        """
        Inspects the fields of the model and returns a dictionary of field names and their types.
        This is useful for dynamically constructing instances of the model.
        """
        return {
            field_name: cls._construct_from_annotation(field_type)()
            for field_name, field_type in cls.model_fields.items()
        }

    @classmethod
    def null(cls: type[Self]) -> Self:
        """
        Returns a null instance of the model with all fields set to None.
        This is useful for cases where no data is expected.
        """
        nulled_data = cls._inspect_fields()
        logging.info(f"Returning {nulled_data}")
        return cls.model_validate(nulled_data)
