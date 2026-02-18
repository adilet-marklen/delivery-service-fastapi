from pydantic import ConfigDict
from pydantic import BaseModel


class ParcelTypeOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
