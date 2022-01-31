from pydantic import BaseModel


class Role(BaseModel):
    id: int
    description: str


class UserBase(BaseModel):
    id: int
    email: EmailStr
    role: Role
    
    class Config:
        orm_mode = True
        

class RoomBase(BaseModel):
    id: int


class UserIn(UserBase):
    first_name: str
    last_name: str
    password: str
    