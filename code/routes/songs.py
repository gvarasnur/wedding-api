"""Module with the routes and endpoints of the API"""
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from bson import ObjectId

from fastapi import APIRouter, Depends
from ..database.mongodb import get_database
from ..helpers.http_error import HTTPError
from ..schemas.invitations import (
    Song,
    SongInDB,
    SongGet
)

router = APIRouter(prefix='/songs',
                   tags=['songs'])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get('/', response_model=list[SongGet])
async def get_songs_list(database=Depends(get_database)):
    """Get all songs"""
    songs = list(database.songs.find({}))
    return songs


@router.get('/{song_id}', response_model=SongGet)
async def get_song(song_id: str, database=Depends(get_database)):
    """Get a song"""
    song = database.songs.find_one({'_id': ObjectId(song_id)})
    if song:
        return song
    raise HTTPError(status_code=404, detail='Song not found')


@router.get('/invitation/{invitation_id}', response_model=list[SongGet])
async def get_songs_for_invitation(invitation_id: str, database=Depends(get_database)):
    """Get all songs for an invitation"""
    songs = list(database.songs.find(
        {'invitation_id': ObjectId(invitation_id)}))
    return songs


@router.post('/', response_model=SongGet)
async def create_song(name: str,
                      invitation_id: str,
                      database=Depends(get_database)):
    """Create a song"""
    # check that invitation exists
    if invitation_id:
        invitation = database.invitations.find_one(
            {'_id': ObjectId(invitation_id)})
        if not invitation:
            raise HTTPError(status_code=400, detail='Invitation not found')

    song = Song(name=name,
                invitation_id=invitation_id)

    song_in_db = SongInDB(
        **song.dict(), **{'created_at': datetime.now()})

    print(song_in_db.dict())
    song_id = database.songs.insert_one(song_in_db.dict()).inserted_id
    song = database.songs.find_one({'_id': song_id})
    return song


@router.put('/{song_id}', response_model=SongGet)
async def update_song(song_id: str, name: str, database=Depends(get_database), token: str = Depends(oauth2_scheme)):
    """Update a song"""
    # check that song exists
    song = database.songs.find_one({'_id': ObjectId(song_id)})
    if not song:
        raise HTTPError(status_code=400, detail='Song not found')

    # update song
    database.songs.update_one(
        {'_id': ObjectId(song_id)}, {'$set': {'name': name}})
    return {'id': song_id, 'name': name}


@router.delete('/{song_id}')
async def delete_song(song_id: str, database=Depends(get_database), token: str = Depends(oauth2_scheme)):
    """Delete a song"""
    result = database.songs.delete_one({'_id': ObjectId(song_id)})
    if result.deleted_count:
        return {'message': 'Song deleted successfully'}
    raise HTTPError(status_code=404, detail='Song not found')
