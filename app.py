from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends, Request
from fastapi_sqlalchemy import DBSessionMiddleware

import schemas
import crud
from configs.database import database, SQL_DATABASE_URL, SessionLocal

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=SQL_DATABASE_URL)


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


@app.get('/')
async def start():
    return {'hello': 'world'}


@app.post('/create_user', response_model=schemas.UserOut)
async def add_new_user(request: Request,
                       new_user: schemas.UserIn,
                       db_session: Session = Depends(get_db)):
    try:
        if request.user.role.description == 'administrator':
            return await crud.create_user(db_session=db_session, new_user=new_user)
        raise PermissionError('You are not allowed to add users')
    except Exception as e:
        return {'error': f'Error type: {type(e).__name__}. Error message: {e}'}


@app.post('/add_room')
async def add_room(new_room: schemas.RoomIn,
                   db_session: Session = Depends(get_db)):
    try:
        return await crud.create_room(db_session=db_session, new_room=new_room)
    except Exception as e:
        return {'error': f'Error type: {type(e).__name__}. Error message: {e}'}
