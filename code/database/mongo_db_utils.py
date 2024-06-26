"""Module for pydantic object creation"""

from bson import ObjectId
import pydantic


class PyObjectId(ObjectId):
    """PyObjectId class used for type verification"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """Validation function"""
        if not ObjectId.is_valid(value):
            raise ValueError('Invalid objectid')
        return ObjectId(value)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str
pydantic.json.ENCODERS_BY_TYPE[PyObjectId] = str
