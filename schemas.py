from datetime import datetime, date
from decimal import Decimal

from pydantic import BaseModel, EmailStr


class Role(BaseModel):
    role_id: int
    role_description: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    id: int
    role: Role
    
    class Config:
        orm_mode = True


class UserIn(BaseModel):
    email: EmailStr
    password: str
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    email: str

    class Config:
        orm_mode = True


class RoomBase(BaseModel):
    room_id: int


class RoomIn(RoomBase):
    space_count: int
    price: int


class RoomBook(RoomBase):
    date_in: date
    date_out: date


class RoomSearch(BaseModel):
    date_in: date
    date_out: date
    space_occupied: int


class BookingInfo(BaseModel):
    number_id: int
