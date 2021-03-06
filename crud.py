from datetime import datetime, date, timedelta

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

import models, schemas


async def get_user_by_email(db_session: Session, user_email: str):
    user = db_session.query(models.User).filter(models.User.email == user_email).first()
    return user


async def get_user_by_id(db_session: Session, user_id: int):
    user = db_session.query(models.User).filter(models.User.user_id == user_id).first()
    return user


async def get_user_by_email_and_password(db_session: Session, user: schemas.UserLogin):
    user = db_session.query(models.User).filter(and_(models.User.email == user.email,
                                                     models.User.password == user.password)).first()
    return user


async def get_all_users_with_roles(db_session: Session):
    users = db_session.execute(select(models.User, models.Role.role_description)
                               .join(models.Role)).fetchall()
    return users


async def get_role_by_description(db_session: Session, role_description: str):
    role = db_session.query(models.Role).filter(models.Role.role_description == role_description).first()
    return role


async def get_all_rooms(db_session: Session):
    rooms = db_session.query(models.Room).all()
    return rooms


async def create_user(db_session: Session, new_user: schemas.UserIn):
    try:
        exist_user = await get_user_by_email(db_session, new_user.email)
        if not exist_user:
            exst_role = await get_role_by_description(db_session, new_user.role)
            if exst_role is None:
                exst_role = models.Role(role_description=new_user.role)
                db_session.add(exst_role)
                db_session.commit()
                db_session.refresh(exst_role)
            user = models.User(email=new_user.email,
                               password=new_user.password, role_id=exst_role.role_id)
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
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
        book_numbers_rooms = await get_all_booking_numbers(db_session=db_session)
        suitable_numbers = []
        for book_number in book_numbers_rooms:
            if book_number.arrival_date and book_number.leaving_date:
                date_in = date(day=book_number.arrival_date.day,
                               month=book_number.arrival_date.month,
                               year=book_number.arrival_date.year)
                date_out = date(day=book_number.leaving_date.day,
                                month=book_number.leaving_date.month,
                                year=book_number.leaving_date.year)
                if date_in == room.date_in and date_out == room.date_out:
                    suitable_numbers.append(book_number.room_key)
        print(book_numbers_rooms, suitable_numbers)
        rooms = db_session.query(models.Room).filter(and_(models.Room.room_id.in_(suitable_numbers),
                                                          models.Room.room_space == room.space_occupied)).all()
        print(rooms)
        return rooms
    except Exception as e:
        raise e


async def get_booking_info(db_session: Session, booking_number: int):
    try:
        booked_num = db_session.query(models.BookNumber).filter(models.BookNumber.number_id == booking_number)
        return booked_num.first()
    except Exception as e:
        raise e


async def get_all_booking_numbers(db_session: Session):
    return db_session.query(models.BookNumber).all()


async def get_booking_numbers_by_room_key(db_session: Session, room_key: int):
    booking_numbers = db_session.query(models.BookNumber).filter(models.BookNumber.room_key == room_key).all()
    return booking_numbers


async def create_booking_number(db_session: Session, new_booking_number: schemas.RoomBook):
    try:
        booking_numbers = await get_booking_numbers_by_room_key(db_session=db_session,
                                                                room_key=new_booking_number.room_id)
        if booking_numbers:
            for number in booking_numbers:
                if number.arrival_date and number.leaving_date:
                    date_in = date(day=number.arrival_date.day,
                                   month=number.arrival_date.month,
                                   year=number.arrival_date.year)
                    date_out = date(day=number.leaving_date.day,
                                    month=number.leaving_date.month,
                                    year=number.leaving_date.year)
                    if (date_in <= new_booking_number.date_in < date_out or
                        date_in < new_booking_number.date_out < date_out):
                        raise ValueError('???????????? ?????????? ????????????????????????!')
            book_num = models.BookNumber(room_key=new_booking_number.room_id,
                                         arrival_date=new_booking_number.date_in,
                                         leaving_date=new_booking_number.date_out)
            db_session.add(book_num)
            db_session.commit()
            db_session.refresh(book_num)
            return book_num
        raise ValueError('?????????? ?????????????? ???? ????????????????????!')
    except Exception as e:
        raise e


async def delete_booking_number(db_session: Session, booking_number_id: int):
    number = await get_booking_info(db_session=db_session, booking_number=booking_number_id)
    if number.arrival_date - datetime.now() > timedelta(days=3):
        db_session.delete(number)
        db_session.commit()
        return '?????????? ??????????'
    return '?????????? ???? ?????????? ???????? ??????????'


async def get_booking_numbers_and_room_info_by_room_id(db_session: Session, room_id: int):
    booking_numbers = db_session.execute(select(models.BookNumber, models.Room)
                                         .join(models.BookNumber)
                                         .where(models.Room.room_id == room_id))
    return booking_numbers.fetchall()
