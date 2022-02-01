from fastapi import FastApi
from fastapi_sqlalchemy import DBSessionMiddleware

from configs.database import database, SQL_DATABASE_URL

app = FastApi()

app.add_middleware(DBSessionMiddleware, db_url=SQL_DATABASE_URL)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/')
async def start():
    return {'hello': 'db_service world'}
