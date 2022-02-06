from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends
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
async def add_new_user(new_user: schemas.UserIn, db_session: Session = Depends(get_db)):
    try:
        return crud.create_user(db_session=db_session, new_user=new_user)
    except Exception as e:
        return {'error': f'Error type: {type(e).__name__}. Error message: {e}'}
