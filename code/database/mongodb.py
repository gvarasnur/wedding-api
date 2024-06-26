"""Database client."""

import mongomock
from decouple import config
from pymongo import MongoClient
from .indexes import configure_database_indexes


MONGODB_URL = config('MONGODB_URL', default=None)
MONGODB_DB_NAME = config('MONGODB_DB_NAME', default=None)

if MONGODB_URL and MONGODB_DB_NAME:
    MONGODB = MongoClient(MONGODB_URL,
                          serverSelectionTimeoutMS=5000)[MONGODB_DB_NAME]
else:
    MONGODB = None


class MongoDB:
    """Database Class"""

    def __init__(self, testing: bool = False):
        if testing:
            self.database = get_mock_database()
        else:
            self.database = get_database()

    def __call__(self):
        return self.database


def get_database() -> MongoClient:
    """Returns real database"""
    return MONGODB


def get_mock_database() -> MongoClient:
    """Returns database for tests"""
    return mongomock.MongoClient()['test_user_db']


def configure_database(database):
    """Function to create database indexes"""
    configure_database_indexes(database)


def clear_database(database: MongoClient):
    """Function to drop database between tests"""
    database.drop_collection('invitations')
