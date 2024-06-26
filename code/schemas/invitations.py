"""Module with the schemas for the service"""

from enum import Enum
from datetime import datetime
from pydantic import Field, BaseModel, validator
from ..database.mongo_db_utils import PyObjectId


class FoodOptionsEnum(str, Enum):
    """Enum with the valid food options"""
    VEGETARIAN = 'vegetarian'
    VEGAN = 'vegan'
    NO_RESTRICTION = 'no restriction'


class Guest(BaseModel):
    """Basic Guest params"""
    name: str
    last_name: str
    is_attending: bool = None
    is_pending: bool = True
    is_kid: bool = False
    menu: FoodOptionsEnum = FoodOptionsEnum.NO_RESTRICTION
    invitation_id: PyObjectId
    with_plus_one: bool = False
    is_plus_one: bool = False


class GuestInDB(Guest):
    """Guest in database"""
    created_at: datetime


class GuestGet(GuestInDB):
    """Basic Guest return"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')

    class Config:
        """Config for GuestGet class"""
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Invitation(BaseModel):
    """Basic Invitation params"""
    name: str
    seen: int = 0


class InvitationEdit(BaseModel):
    """Basic Invitation params input"""

    class Config:
        """Config for InvitationEdit class"""
        arbitrary_types_allowed = True


class InvitationInDB(Invitation):
    """Invitation in database"""
    created_at: datetime


class InvitationGet(InvitationInDB):
    """Basic Invitation return"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    guests: list[GuestGet]

    class Config:
        """Config for InvitationGet class"""
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Song(BaseModel):
    """Basic Song params"""
    name: str
    invitation_id: PyObjectId


class SongInDB(Song):
    """Song in database"""
    created_at: datetime


class SongGet(SongInDB):
    """Basic Song return"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')

    class Config:
        """Config for SongGet class"""
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
