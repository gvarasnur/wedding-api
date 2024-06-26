"""Errors module."""

from fastapi import status
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic.error_wrappers import ValidationError
from bson.errors import InvalidId


async def validation_exception_handler(_, exc: ValidationError):
    """Handle validation errors."""

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'detail': exc.errors(), 'body': exc.json()}),
    )


async def validation_exception_bson_handler(_, exc: InvalidId):
    """Handle validation errors."""

    print(exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'detail': exc, 'body': exc}),
    )
