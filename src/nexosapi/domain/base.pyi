import typing
from pydantic import BaseModel

class NullableBaseModel(BaseModel):
    """
    Base model that allows fields to be None.
    This is useful for cases where fields may not always have a value.
    """
    @classmethod
    def null(cls) -> typing.Self:
        """
        Returns a null instance of the model with all fields set to None.
        This is useful for cases where no data is expected.
        """
