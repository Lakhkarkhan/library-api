from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str


class RoleUpdate(BaseModel):
    role: Literal["user", "admin"]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    isbn: str | None = Field(default=None, max_length=20)
    year: int | None = Field(default=None, ge=0, le=2100)


class BookCreate(BookBase):
    pass


class BookOut(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int
