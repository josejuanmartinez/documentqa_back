from typing import Union

from pydantic import BaseModel


class GenericSchema(BaseModel):
    message: str
    result: Union[str, dict]
    code: int
