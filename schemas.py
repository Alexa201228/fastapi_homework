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
        

class RoomBase(BaseModel):
    id: int


class UserIn(UserBase):
    email: EmailStr
    password: str


class UserOut(UserBase):
    email: str

    class Config:
        orm_mode = True
