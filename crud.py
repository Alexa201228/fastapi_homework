from sqlalchemy import and_
from sqlalchemy.orm import Session

import models, schemas


async def get_user_by_email(db_session: Session, user_email: str):
    user = db_session.query(models.User).filter(models.User.email == user_email).first()
    if user:
        return user
    raise KeyError('User with this email does not exist')


async def create_user(db_session: Session, new_user: schemas.UserIn):
    try:
        exist_user = await get_user_by_email(db_session, new_user.email)
        if not exist_user:
            user_role = models.Role(role_id=new_user.role.role_id,
                                    role_description=new_user.role.role_description)
            db_session.add(user_role)
            user = models.User(email=new_user.email,
                               password=new_user.password, role=user_role)
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            db_session.refresh(user_role)
            return user
        raise ValueError("User already exists!")
    except Exception as e:
        db_session.rollback()
        raise e


async def create_room(db_session: Session, new_room: schemas.RoomIn):
    """
    Endpoint to create a new room\n
    :param new_room: New room with id (should be unique), space_count and price
    :return:
    """
    try:
        room = models.Room(room_id=new_room.room_id,
                           room_space=new_room.space_count,
                           price_for_night=new_room.price)

        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)
    except Exception as e:
        raise e


async def search_room_by_dates_and_space(db_session: Session, room: schemas.RoomSearch):
    """
    Endpoint to search rooms by its' in and out dates and room space
    :param db_session: Current db session
    :param room: Room for searching
    :return:
    """
    try:
        book_numbers_rooms = db_session.query(models.BookNumber.room.room_id)\
            .filter(and_(models.BookNumber.room.room_space == room.space_occupied,
                         models.BookNumber.arrival_date == room.date_in,
                         models.BookNumber.leaving_date == room.date_out)).fetchall()
        rooms = db_session.query(models.Room).filter(models.Room.room_id.in_(book_numbers_rooms)).fetchall()
        return rooms
    except Exception as e:
        raise e
