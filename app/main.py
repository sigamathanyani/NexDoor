from fastapi import FastAPI
from app.database.db import Base, engine
from app.routes.auth_routes import router as auth_router
from app.routes.product_routes import router as product_router

app = FastAPI()

app.include_router(auth_router, prefix='/auth')
app.include_router(product_router, prefix='/products')


Base.metadata.create_all(bind=engine)