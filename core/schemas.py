from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr, conint, Field
from typing import Annotated, Optional


class PostBase(BaseModel):
    title: Annotated[str, "must be a string"]
    content: str
    published: bool = True


class CreatePost(PostBase):
    pass


class UpdatePost(PostBase):
    pass


class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    created_at: datetime

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "created_at": self.created_at,
        }


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    class Config:
        arbitrary_types_allowed = True


class ReturnUser(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "created_at": self.created_at,
        }

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class PostResponse(PostBase):
    id: uuid.UUID
    created_at: datetime
    owner_id: uuid.UUID
    owner: Optional[ReturnUser]

    class Config:
        orm_mode = True


class PostWithLikes(BaseModel):
    post: PostResponse
    likes: int

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str


class UserInDB(User):
    password: str


class Vote(BaseModel):
    post_id: uuid.UUID
    dir: int = Field(..., ge=0, le=1)
