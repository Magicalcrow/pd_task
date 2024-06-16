from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
	id: int
	username: str
	
	class Config:
		orm_mode = True

class GistBase(BaseModel):
	gist_id: str
	description: str
	user_id: int
	is_new: bool

	class Config:
		orm_mode = True

class UserWithGists(UserBase):
	gists: List[GistBase] = []

	class Config:
		orm_mode = True
