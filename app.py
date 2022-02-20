from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.templating import Jinja2Templates

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
async def start(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'hello': 'world'})


@app.post('/login')
async def login(response: Response, user: schemas.UserLogin, db_session: Session = Depends(get_db)):
    try:
        user = await crud.get_user_by_email_and_password(db_session=db_session, user=user)
        if user is None:
            raise Exception('Wrong email or password')
        return user
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': f'Error type: {type(e).__name__}. Error message: {e}'}


@app.post('/create_user')
async def add_new_user(request: Request,
                       new_user: schemas.UserIn,
                       response: Response,
                       db_session: Session = Depends(get_db)):
    try:
        #TODO: identify user
        print(request.state)
        if request.state['user'].role.role_description == 'administrator':
            return await crud.create_user(db_session=db_session, new_user=new_user)
        raise PermissionError('You are not allowed to add users')
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': f'Error type: {type(e).__name__}. Error message: {e}'}


@app.get('/employees', response_class=HTMLResponse)
async def get_all_employees(request: Request, db_session: Session = Depends(get_db)):
    try:
        employees = await crud.get_all_users_with_roles(db_session=db_session)
        return templates.TemplateResponse('employees.html', {'request': request, 'employees': employees})
    except Exception as e:
        return templates.TemplateResponse('400_error.html',
                                          {'request': request, 'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.post('/add_room')
async def add_room(new_room: schemas.RoomIn,
                   response: Response,
                   db_session: Session = Depends(get_db)):
    try:
        return await crud.create_room(db_session=db_session, new_room=new_room)
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': f'Error type: {type(e).__name__}. Error message: {e}'}


@app.get('/search_room')
async def search_rooms(request: Request,
                       room_search: schemas.RoomSearch, db_session: Session = Depends(get_db)):
    try:
        return await crud.search_room_by_dates_and_space(db_session=db_session, room=room_search)
    except Exception as e:
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.get('/rooms', response_class=HTMLResponse)
async def get_all_rooms(request: Request, db_session: Session = Depends(get_db)):
    try:
        rooms = await crud.get_all_rooms(db_session=db_session)
        return templates.TemplateResponse('rooms.html', {'request': request, 'rooms': rooms})
    except Exception as e:
        return templates.TemplateResponse('400_error.html',
                                          {'request': request,
                                           'error': f'Error type: {type(e).__name__}. Error message: {e}'})


@app.get('/booking_number_info')
async def get_booking_number_info(response: Response,
                                  booking_num: int,
                                  db_session: Session = Depends(get_db)):
    try:
        booked_num = await crud.get_booking_info(db_session=db_session, booking_number=booking_num)
        if booked_num is not None:
            return booked_num
        raise Exception('Номер брони с таким идентификатором не существует!')
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': f'Error type: {type(e).__name__}. Error message: {e}'}
