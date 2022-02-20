from datetime import datetime
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


class UserIn(UserBase):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    email: str

    class Config:
        orm_mode = True


class RoomBase(BaseModel):
    room_id: int

    class Config:
        orm_mode = True


class RoomIn(RoomBase):
    space_count: int
    price: Decimal


class RoomSearch(BaseModel):
    date_in: datetime
    date_out: datetime
    space_occupied: int


class BookingInfo(BaseModel):
    number_id: int
