from datetime import datetime, date

from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends, Request, Response, status, Form
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

import schemas
import crud
from configs.database import database, SQL_DATABASE_URL, SessionLocal


app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=SQL_DATABASE_URL)

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/', response_class=HTMLResponse)
async def start(request: Request, db_session: Session = Depends(get_db)):
    if request.cookies.get('user_id'):
        user = await crud.get_user_by_id(db_session, int(request.cookies.get('user_id')))
        return templates.TemplateResponse('index.html', {'request': request, 'user': user})
    return templates.TemplateResponse('index.html', {'request': request, 'hello': 'world'})


@app.get('/login')
async def redirect_login():
    return RedirectResponse('/')


@app.get('/logout')
async def logout():
    response = RedirectResponse('/')
    response.delete_cookie('user_id')
    return response


@app.post('/login')
async def login(request: Request, response: Response, user_email: str = Form(...),
                password: str = Form(...), db_session: Session = Depends(get_db)):
    try:
        user_in = schemas.UserLogin(email=user_email, password=password)
        user = await crud.get_user_by_email_and_password(db_session=db_session, user=user_in)
        if user is None:
            raise Exception('Wrong email or password')
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        response.set_cookie('user_id', user.user_id)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.post('/create_user')
async def add_new_user(request: Request,
                       response: Response,
                       user_email: str = Form(...), role: str = Form(...),
                       password: str = Form(...),
                       db_session: Session = Depends(get_db)):
    try:
        if request.cookies.get('user_id'):
            user = await crud.get_user_by_id(db_session, int(request.cookies.get('user_id')))
            if user.role.role_description == 'administrator':
                if role != 'administrator':
                    new_user = schemas.UserIn(email=user_email, password=password, role=role)
                    await crud.create_user(db_session=db_session, new_user=new_user)
                    return RedirectResponse('/employees', status_code=status.HTTP_302_FOUND)
                raise PermissionError('Добавлять можно только менеджеров!')
            raise PermissionError('You are not allowed to add users!')
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.get('/employees', response_class=HTMLResponse)
async def get_all_employees(request: Request, response: Response, db_session: Session = Depends(get_db)):
    try:
        if request.cookies.get('user_id'):
            employees = await crud.get_all_users_with_roles(db_session=db_session)
            return templates.TemplateResponse('employees.html', {'request': request, 'employees': employees})
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return templates.TemplateResponse('400_error.html',
                                          {'request': request, 'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.post('/add_room')
async def add_room(request: Request,
                   response: Response,
                   room_number: int = Form(...),
                   room_space: int = Form(...),
                   price: int = Form(...),
                   db_session: Session = Depends(get_db)):
    try:
        if request.cookies.get('user_id'):
            new_room = schemas.RoomIn(room_id=room_number, space_count=room_space, price=price)
            await crud.create_room(db_session=db_session, new_room=new_room)
            response = RedirectResponse('/rooms', status_code=status.HTTP_302_FOUND)
            return response
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': f'Error type: {type(e).__name__}. Error message: {e}'}


@app.get('/search_room')
async def search_rooms(request: Request, response: Response):
    try:
        if request.cookies.get('user_id'):
            return templates.TemplateResponse('find_room.html', {'request': request})
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.post('/search_room')
async def search_rooms(request: Request,
                       response: Response,
                       date_in: date = Form(...),
                       date_out: date = Form(...),
                       room_space: int = Form(...),
                       db_session: Session = Depends(get_db)):
    try:
        if request.cookies.get('user_id'):
            if date_out <= date_in:
                raise Exception('Дата заезда должна быть раньше даты отъезда!')
            room_search = schemas.RoomSearch(date_in=date_in, date_out=date_out, space_occupied=room_space)
            found_rooms = await crud.search_room_by_dates_and_space(db_session=db_session, room=room_search)
            return templates.TemplateResponse('find_room.html', {'request': request, 'rooms': found_rooms})
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.get('/rooms', response_class=HTMLResponse)
async def get_all_rooms(request: Request, response: Response, db_session: Session = Depends(get_db)):
    try:
        if request.cookies.get('user_id'):
            rooms = await crud.get_all_rooms(db_session=db_session)
            return templates.TemplateResponse('rooms.html', {'request': request, 'rooms': rooms})
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.get('/booking_number_info')
async def get_booking_number_info(response: Response, request: Request):
    try:
        if request.cookies.get('user_id'):
            return templates.TemplateResponse('find_booked_number.html', {'request': request})
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': f'Error type: {type(e).__name__}. Error message: {e}'}


@app.post('/booking_number_info')
async def get_booking_number_info(response: Response,
                                  request: Request,
                                  booking_num: int = Form(...),
                                  db_session: Session = Depends(get_db)):
    try:
        if request.cookies.get('user_id'):
            booked_num = await crud.get_booking_info(db_session=db_session, booking_number=booking_num)
            if booked_num is not None:
                return templates.TemplateResponse('find_booked_number.html',
                                                  {'request': request, 'booking_number': booked_num})
            raise Exception('Номер брони с таким идентификатором не существует!')
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': f'Error type: {type(e).__name__}. Error message: {e}'}


@app.get('/booking_numbers')
async def get_booking_numbers(request: Request, response: Response):
    try:
        if request.cookies.get('user_id'):
            return templates.TemplateResponse('booking.html', {'request': request})
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.post('/add_booking_number')
async def add_booking_number(request: Request, response: Response,
                             room_number: int = Form(...),
                             date_in: date = Form(...),
                             date_out: date = Form(...),
                             db_session: Session = Depends(get_db)):
    try:
        if request.cookies.get('user_id'):
            if date_out <= date_in:
                raise Exception('Дата заезда должна быть раньше даты отъезда!')
            new_booking = schemas.RoomBook(room_id=room_number, date_in=date_in, date_out=date_out)
            created_number = await crud.create_booking_number(db_session=db_session, new_booking_number=new_booking)
            return templates.TemplateResponse('booking.html', {'request': request, 'booking_rooms': [created_number]})
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.post('/delete_booking_number')
async def delete_booking_number(request: Request, response: Response,
                                deleting_number: int = Form(...),
                                db_session: Session = Depends(get_db)):
    try:
        if request.cookies.get('user_id'):
            deleted_booking_number = await crud.delete_booking_number(db_session=db_session, booking_number_id=deleting_number)
            return templates.TemplateResponse('delete_booked_number.html', {'request': request,
                                                                            'delete_result': deleted_booking_number})
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.get('/delete_booking_number')
async def delete_booking_number(request: Request, response: Response):
    try:
        if request.cookies.get('user_id'):
            return templates.TemplateResponse('delete_booked_number.html', {'request': request})
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.get('/get_all_room_bookings')
async def get_all_room_booking_numbers(request: Request, response: Response):
    try:
        if request.cookies.get('user_id'):
            return templates.TemplateResponse('room_bookings.html', {'request': request})
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.post('/get_all_room_bookings')
async def get_all_room_booking_numbers(request: Request, response: Response,
                                       room_number: int = Form(...),
                                       db_session: Session = Depends(get_db)):
    try:
        if request.cookies.get('user_id'):
            booked_numbers = await crud.get_booking_numbers_and_room_info_by_room_id(db_session=db_session,
                                                                                     room_id=room_number)
            return templates.TemplateResponse('room_bookings.html', {'request': request, 'rooms': booked_numbers})
        response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})
