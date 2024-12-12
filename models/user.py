from pydantic import BaseModel, Field
from typing import List

class User(BaseModel):
    username: str
    key: str
    posts: List = Field(default_factory=list)
