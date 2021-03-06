from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import CheckConstraint

from configs.database import Base


class Role(Base):

    __tablename__ = 'role'

    role_id = Column(Integer, primary_key=True, index=True)
    role_description = Column(String)


class BookNumber(Base):

    __tablename__ = 'book_number'

    number_id = Column(Integer, primary_key=True, index=True)
    arrival_date = Column(DateTime(timezone=True))
    leaving_date = Column(DateTime(timezone=True))
    room_key = Column(Integer, ForeignKey('room.room_id', name='fk_room_book_number_room_id'))

    __table_args__ = (
        CheckConstraint('arrival_date < leaving_date'),
    )


class Room(Base):

    __tablename__ = 'room'

    room_id = Column(Integer, primary_key=True, index=True)
    room_space = Column(Integer, default=1)
    price_for_night = Column(Integer)
    book_numbers = relationship('BookNumber', backref=backref('room'))


class User(Base):

    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    role_id = Column(Integer, ForeignKey('role.role_id'))

    role = relationship('Role', backref=backref('users', lazy='dynamic'))
