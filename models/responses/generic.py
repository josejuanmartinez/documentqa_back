from pydantic import BaseModel


class Generic(BaseModel):
    message: str
    result: str
    code: int
