from fastapi import FastAPI
from app.database.db import Base, engine
from app.routes.auth_routes import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix='/auth')


Base.metadata.create_all(bind=engine)