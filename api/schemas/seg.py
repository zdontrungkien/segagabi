from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, Field
from typing import Optional


class ObjectIdField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        try:
            return ObjectId(str(value))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")


class Document(BaseModel):
    user: str = Field(...)
    date: str = Field(...)
    title: str = Field(...)
    content: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UpdateDocument(BaseModel):
    user: Optional[str]
    date: Optional[str]
    title: Optional[str]
    content: Optional[str]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DocumentResponse(Document):
    id: ObjectIdField = Field(...)
