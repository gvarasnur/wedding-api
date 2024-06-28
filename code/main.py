"""Main entrypoint for the FastAPI application."""
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from pydantic.error_wrappers import ValidationError
from bson.errors import InvalidId

from .routes import invitations, health, guests, songs
from .database.mongodb import configure_database, get_database

from .errors import validation_exception_handler
from .errors import validation_exception_bson_handler

# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}


app = FastAPI(title='Invitations Service', version='0.0.1')

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app.include_router(invitations.router)
app.include_router(guests.router)
app.include_router(health.router)
app.include_router(songs.router)

app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(InvalidId, validation_exception_bson_handler)


DB = get_database()

configure_database(DB)


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint for the FastAPI application."""
    user_name = form_data.username
    password = form_data.password
    user_from_env = os.getenv('ADMIN_USERNAME')
    password_from_env = os.getenv('ADMIN_PASSWORD')
    if user_name == user_from_env and password == password_from_env:
        return {"access_token": user_name, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
