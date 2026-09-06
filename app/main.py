from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.database.db import Base, engine
from app.routes.auth_routes import router as auth_router
from app.routes.product_routes import router as product_router
from app.routes.media_routes import router as media_router
from app.exceptions.app_exception import AppException
from app.schemas.exception_schema import ExceptionResponse
from app.utils.error_codes import ErrorCode

app = FastAPI()


@app.exception_handler(AppException)
def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        content=ExceptionResponse(
            message=exc.message,
            error_code=exc.error_code,
        ).model_dump(),
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
def request_validation_exception_handler(request: Request, exc: RequestValidationError):

    errors = exc.errors()
    all_errors = []
    for e in errors:
        all_errors.append(
            ExceptionResponse(
                message=f"{e['loc'][1]}. {e['msg']}",
                error_code=ErrorCode.VALIDATION_ERROR,
            ).model_dump()
        )

    return JSONResponse(
        content={"Errors": all_errors},
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


app.include_router(auth_router, prefix="/auth")
app.include_router(product_router, prefix="/products")
app.include_router(media_router, prefix="/media")


Base.metadata.create_all(bind=engine)
