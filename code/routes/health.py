"""Module with health check routes and endpoints of the API"""
from fastapi import APIRouter, HTTPException, Query, Depends
from ..database.mongodb import get_database, MongoDB
from pymongo.errors import ConnectionFailure


router = APIRouter(tags=['health'])


@router.get('/ping', description='Check if the API is alive')
async def ping():
    """Endpoint to check if the API is alive"""
    return 'pong'


@router.get('/health', description='Check if the API is ready')
async def read(mongodb: MongoDB = Depends(get_database)):
    """Endpoint to check if the API is ready"""
    try:
        mongodb.command('ping')
        return {"message": "MongoDB connection successful!"}
    except ConnectionFailure:
        return {"message": "Failed to connect to MongoDB."}
