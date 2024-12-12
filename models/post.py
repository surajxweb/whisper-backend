from pydantic import BaseModel, Field
from typing import List

class Post(BaseModel):
    title: str
    author: str
    description: str
    topic: str
    fileUrl: str = None
    responses:List = Field(default_factory=list)
