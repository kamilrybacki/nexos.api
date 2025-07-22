from pydantic import BaseModel

class NullableBaseModel(BaseModel):
    @classmethod
    def null(cls) -> NullableBaseModel: ...
