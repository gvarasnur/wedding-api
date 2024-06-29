"""Module with the routes and endpoints of the API"""
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from bson import ObjectId

from fastapi import APIRouter, Depends
from ..database.mongodb import get_database
from ..helpers.http_error import HTTPError
from ..schemas.invitations import (
    FoodOptionsEnum,
    Guest,
    GuestInDB,
    GuestGet
)

router = APIRouter(prefix='/guests',
                   tags=['guests'])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get('/', response_model=list[GuestGet])
async def get_guests(database=Depends(get_database)):
    """Get all guests"""
    guests = list(database.guests.find({}))
    return guests


@router.get('/{guest_id}', response_model=GuestGet)
async def get_guest(guest_id: str, database=Depends(get_database)):
    """Get a guest"""
    guest = database.guests.find_one({'_id': ObjectId(guest_id)})
    if guest:
        return guest
    raise HTTPError(status_code=404, detail='Guest not found')


@router.post('/')
async def create_guest(name: str,
                       last_name: str,
                       invitation_id: str,
                       is_confirmed: bool = False,
                       is_pending: bool = True,
                       is_kid: bool = False,
                       menu: FoodOptionsEnum = FoodOptionsEnum.NO_RESTRICTION,
                       with_plus_one: bool = False,
                       is_plus_one: bool = False,
                       database=Depends(get_database), token: str = Depends(oauth2_scheme)):
    """Create a guest"""
    # check that invitation exists
    if invitation_id:
        invitation = database.invitations.find_one(
            {'_id': ObjectId(invitation_id)})
        if not invitation:
            raise HTTPError(status_code=400, detail='Invitation not found')

    guest = Guest(name=name,
                  last_name=last_name,
                  is_confirmed=is_confirmed,
                  is_pending=is_pending,
                  is_kid=is_kid,
                  menu=menu,
                  with_plus_one=with_plus_one,
                  invitation_id=invitation_id,
                  is_plus_one=is_plus_one)
    guest_in_db = GuestInDB(**guest.dict(), created_at=datetime.now())
    created_id = database.guests.insert_one(guest_in_db.dict()).inserted_id
    guest = database.guests.find_one({'_id': created_id})
    return guest


@router.patch('/{guest_id}')
async def update_guest(guest_id: str,
                       inivitation_id: str = None,
                       name: str = None,
                       last_name: str = None,
                       is_confirmed: bool = None,
                       is_pending: bool = None,
                       is_kid: bool = None,
                       menu: FoodOptionsEnum = None,
                       with_plus_one: bool = None,
                       is_plus_one: bool = None,
                       database=Depends(get_database),
                       token: str = Depends(oauth2_scheme)):
    """Update a guest"""
    fields_to_update = {}

    # Add each field to the dictionary only if its value is not None
    if is_confirmed is not None:
        fields_to_update['is_confirmed'] = is_confirmed
    if is_pending is not None:
        fields_to_update['is_pending'] = is_pending
    if is_kid is not None:
        fields_to_update['is_kid'] = is_kid
    if menu is not None:
        fields_to_update['menu'] = menu
    if with_plus_one is not None:
        fields_to_update['with_plus_one'] = with_plus_one
    if is_plus_one is not None:
        fields_to_update['is_plus_one'] = is_plus_one
    if name is not None:
        fields_to_update['name'] = name
    if last_name is not None:
        fields_to_update['last_name'] = last_name
    if inivitation_id is not None:
        fields_to_update['invitation_id'] = ObjectId(inivitation_id)

    # Perform the update operation with the fields to update
    result = database.guests.update_one(
        {'_id': ObjectId(guest_id)},
        {'$set': fields_to_update}
    )
    if result.modified_count:
        guest = database.guests.find_one({'_id': ObjectId(guest_id)})
        return guest
    raise HTTPError(status_code=404, detail='Guest not found')


@router.delete('/{guest_id}')
async def delete_guest(guest_id: str, database=Depends(get_database), token: str = Depends(oauth2_scheme)):
    """Delete a guest"""
    result = database.guests.delete_one({'_id': ObjectId(guest_id)})
    if result.deleted_count:
        return {'message': 'Guest deleted successfully'}
    raise HTTPError(status_code=404, detail='Guest not found')


@router.patch('/{guest_id}/confirm')
async def confirm_guest(guest_id: str, menu: FoodOptionsEnum, database=Depends(get_database)):
    """Confirm a guest"""
    result = database.guests.update_one(
        {'_id': ObjectId(guest_id)}, {'$set': {'is_confirmed': True, 'menu': menu, 'is_pending': False}})
    if result.modified_count:
        guest = database.guests.find_one({'_id': ObjectId(guest_id)})
        return guest
    raise HTTPError(status_code=404, detail='Guest not found')
