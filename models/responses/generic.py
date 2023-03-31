from typing import Union

from pydantic import BaseModel


class Generic(BaseModel):
    message: str
    result: Union[str, dict]
    code: int
