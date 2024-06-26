from pydantic import BaseModel


class HTTPError(BaseModel):
    """Basic Error class"""
    detail: str

    class Config:
        """Config for HTTPError class"""
        schema_extra = {'example': {'detail': 'HTTPException raised.'}}
