from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .configs.database import Base


class Role(Base):

    __tablename__ = 'role'

    role_id = Column(Integer, primary_key=True, index=True)
    role_description = Column(String)


class Room(Base):

    __tablename__ = 'room'

    room_id = Column(Integer, primary_key=True, index=True)
