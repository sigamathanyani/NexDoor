from fastapi import FastAPI
from app.config import settings
from app.database.db import Base, engine

app = FastAPI()

@app.get('/')
def home():
    return {'home': settings.database_url}


Base.metadata.create_all(bind=engine)