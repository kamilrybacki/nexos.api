from __future__ import annotations

import logging
import typing
from collections.abc import Callable  # noqa: TC003
from types import NoneType
from typing import Any, Literal

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic.main import IncEx  # noqa: TC002
from pydantic_core._pydantic_core import PydanticUndefined, PydanticUndefinedType


class NullableBaseModel(BaseModel):
    """
    Base model that allows fields to be None.
    This is useful for cases where fields may not always have a value.
    """

    @classmethod
    def _construct_from_annotation(cls, field: FieldInfo | NullableBaseModel | type) -> typing.Any:
        """
        Constructs a field from its annotation.
        If the field has a default value, it will be used as the return value.
        If the field type is a Union or has an origin, it will be handled accordingly,
        meaning that only the first type in the Union will be used.
        Otherwise, it will return the field name and its type as a tuple.


        :param field: The type of the field.
        :return: A tuple containing the field name and its type.
        """
        if hasattr(field, "null"):
            return field.null

        field = field.annotation if isinstance(field, FieldInfo) else field  # type: ignore[assignment]

        if hasattr(field, "null"):
            return field.null

        if hasattr(field, "default") and not isinstance(field.default, (PydanticUndefinedType, PydanticUndefined)):  # type: ignore
            return field.default

        if hasattr(field, "__name__") and "Literal" in field.__name__:
            return None

        # Try to call the origin if it is callable.
        # This is useful for cases where the origin is a class or function
        # that can be instantiated or called without arguments.

        # In case of types which cannot be instantiated, we skip returning the origin
        # and proceed with the next checks.
        origin = typing.get_origin(field)
        try:
            origin()  # type: ignore
        except TypeError:
            field_args = typing.get_args(field)
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

        :return: A dictionary mapping field names to their default values.
        """
        fields = {}
        for field_name, field_type in cls.model_fields.items():
            constructor = cls._construct_from_annotation(field_type.annotation)  # type: ignore
            if constructor is not None:
                fields[field_name] = constructor()
        return fields

    @classmethod
    def null(cls: type[typing.Self], quiet: bool = True) -> typing.Self:
        """
        Returns a null instance of the model with all fields set to None.
        This is useful for cases where no data is expected.

        :param quiet: If True, suppresses logging of the null response (default: True)
        :return: A null instance of the model with all fields set to None.
        """
        nulled_data = cls._inspect_fields()
        non_empty_fields_data = {k: v for k, v in nulled_data.items() if v is not None}
        if not quiet:
            logging.warning(f"[SDK] Returning null response: {non_empty_fields_data}")
        return cls.model_validate(non_empty_fields_data)

    def model_dump(  # noqa: PLR0913
        self,
        *,
        mode: Literal["json", "python"] = "python",  # type: ignore
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,  # noqa: ARG002
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        fallback: Callable[[Any], Any] | None = None,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        """
        Dumps the model to a dictionary, excluding fields that are None.

        :param mode: The mode to use for dumping the model (json or python).
        :param include: Fields to include in the output.
        :param exclude: Fields to exclude from the output.
        :param context: Contextual information to include in the output.
        :param by_alias: Whether to use field aliases in the output.
        :param exclude_unset: Whether to exclude unset fields from the output.
        :param exclude_defaults: Whether to exclude fields with default values from the output.
        :param exclude_none: Whether to exclude fields with None values from the output.
        :param round_trip: Whether to enable round-trip serialization.
        :param warnings: Warning level for the serialization process.
        :param fallback: Fallback function to call in case of serialization errors.
        :param serialize_as_any: Whether to serialize the model as "any" type.

        :return: A dictionary representation of the model.
        """
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=True,
            round_trip=round_trip,
            warnings=warnings,
            fallback=fallback,
            serialize_as_any=serialize_as_any,
        )
