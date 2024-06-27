"""Module with the routes and endpoints of the API"""
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from bson import ObjectId

from fastapi import APIRouter, Depends, HTTPException
from ..database.mongodb import get_database
from ..schemas.invitations import (
    InvitationInDB,
    Invitation,
    InvitationGet,
)

router = APIRouter(prefix='/invitations',
                   tags=['invitations'])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_guests_for_invitation(invitation_id, database):
    """Get all guests for an invitation"""
    guests = list(database.guests.find(
        {'invitation_id': ObjectId(invitation_id)}))
    return guests


def get_guest_from_list(invitation_id, guests):
    """Get all guests for an invitation"""
    for guest in guests:
        invitation_id = guest.get('invitation_id')
        if not invitation_id:
            raise HTTPException(
                status_code=400, detail='Invitation id is required')

        if guest['invitation_id'] == ObjectId(invitation_id):
            return guest
    return None


def check_guests_in_invitation(invitation_guest, guests):
    """Check that all guests are in the invitation"""
    invitation_guest_ids = [str(guest['_id']) for guest in invitation_guest]
    for guest in guests:
        if guest['_id'] not in invitation_guest_ids:
            return False
    return True


@router.get('/', response_model=list[InvitationGet])
async def get_invitations(database=Depends(get_database)):
    """Get all invitations"""
    invitations = list(database.invitations.find({}))
    # for each invitation, search the guests and add them to the invitation
    for invitation in invitations:
        guests = get_guests_for_invitation(invitation['_id'], database)
        invitation['guests'] = guests

    return invitations


@router.post('/')
async def create_empty_invitation(name: str, database=Depends(get_database), token: str = Depends(oauth2_scheme)):
    """Create an empty invitation"""
    # check that name is not empty and unique
    if not name:
        raise HTTPException(status_code=400, detail='Name is required')
    if database.invitations.find_one({'name': name}):
        raise HTTPException(status_code=400, detail='Name is not unique')

    empty_invitation_in_db = InvitationInDB(
        **{'created_at': datetime.now(), 'name': name})

    created_id = database.invitations.insert_one(
        empty_invitation_in_db.dict()).inserted_id

    invitation = database.invitations.find_one({'_id': created_id})
    invitation['guests'] = []

    return invitation


@router.delete('/{invitation_id}')
async def delete_invitation(invitation_id: str, database=Depends(get_database), token: str = Depends(oauth2_scheme)):
    """Delete an invitation"""
    result = database.invitations.delete_one({'_id': ObjectId(invitation_id)})
    if result.deleted_count:
        return {'message': 'Invitation deleted successfully'}
    raise HTTPException(status_code=404, detail='Invitation not found')


@router.get('/{invitation_id}')
async def get_invitation(invitation_id: str, database=Depends(get_database)):
    """Get a single invitation"""
    invitation = database.invitations.find_one(
        {'_id': ObjectId(invitation_id)})
    if invitation:
        guests = get_guests_for_invitation(invitation_id, database)
        invitation['guests'] = guests
        return invitation
    raise HTTPException(status_code=404, detail='Invitation not found')


@router.get('/by_name/{name}', response_model=InvitationGet)
async def get_invitation_by_name(name: str, database=Depends(get_database)):
    """Get a single invitation by name"""
    invitation = database.invitations.find_one(
        {'name': name})
    if invitation:
        guests = get_guests_for_invitation(invitation['_id'], database)
        invitation['guests'] = guests
        # add 1 to seen counter
        database.invitations.update_one(
            {'_id': invitation['_id']},
            {'$inc': {'seen': 1}}
        )

        # return the updated invitation
        invitation = database.invitations.find_one(
            {'_id': invitation['_id']})

        return invitation
    raise HTTPException(status_code=404, detail='Invitation not found')


@router.get('/by_guest_name/', response_model=InvitationGet)
async def get_invitation_by_guest_name(name: str = '', last_name: str = '', database=Depends(get_database)):
    """Get a single invitation by guest name"""
    if not name or not last_name:
        raise HTTPException(status_code=400,
                            detail='Name and last_name is required')

    guest = database.guests.find_one(
        {'name': name, 'last_name': last_name})
    if guest:
        invitation = database.invitations.find_one(
            {'_id': guest['invitation_id']})
        guests = get_guests_for_invitation(invitation['_id'], database)
        invitation['guests'] = guests

        # add 1 to seen counter
        database.invitations.update_one(
            {'_id': invitation['_id']},
            {'$set': {'seen': invitation['seen'] + 1}}
        )
        return invitation

    raise HTTPException(status_code=404, detail='Invitation not found')


@router.post('/{invitation_id}/guests/confirm', response_model=InvitationGet)
async def confirm_guests(invitation_id: str,
                         guests: list[dict],
                         new_guests: list[dict] = None,
                         database=Depends(get_database)):
    """Confirm all guests for an invitation"""
    # check that the invitation exists
    invitation = database.invitations.find_one(
        {'_id': ObjectId(invitation_id)})
    if not invitation:
        raise HTTPException(status_code=404, detail='Invitation not found')

    invitation_guests = get_guests_for_invitation(invitation_id, database)
    count_max_new_guests = 0
    # check that the guests exist
    for guest in invitation_guests:
        if not guest:
            raise HTTPException(status_code=404, detail='Guest not found')
        if guest and guest.get('with_plus_one'):
            count_max_new_guests += 1
        if guest and guest.get('is_plus_one'):
            count_max_new_guests -= 1

    # check that guest to update are in the invitation
    if not check_guests_in_invitation(invitation_guests, guests):
        raise HTTPException(
            status_code=400, detail='Guest not in the invitation')

    # check that the new guests are not more than the allowed
    new_guest_length = 0
    if new_guests not in [None, []]:
        new_guest_length = len(new_guests)

    if new_guest_length > count_max_new_guests:
        raise HTTPException(status_code=400, detail='Too many new guests')

    # update the guests and check if the guests are from the invitation

    for guest in guests:
        id = guest.get('_id')
        is_attending = guest.get('is_attending')
        menu = guest.get('menu')
        database.guests.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'is_attending': is_attending,
                'menu': menu,
                'is_pending': False
            }}
        )

    # create the new guests
    if new_guests not in [None, []]:
        for new_guest in new_guests:
            new_guest['invitation_id'] = ObjectId(invitation_id)
            new_guest['is_attending'] = True
            new_guest['created_at'] = datetime.now()
            new_guest['is_plus_one'] = True
            new_guest['is_pending'] = False
            database.guests.insert_one(new_guest)

    # return the updated invitation
    invitation = database.invitations.find_one(
        {'_id': ObjectId(invitation_id)})
    guests = get_guests_for_invitation(invitation_id, database)
    invitation['guests'] = guests
    return invitation
