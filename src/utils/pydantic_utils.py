from pydantic import BaseModel as DefaultModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class BaseModel(DefaultModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="ignore",
    )


class BaseSchemaModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
