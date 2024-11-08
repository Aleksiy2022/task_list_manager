from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from .routers import auth, tasks

http_bearer = HTTPBearer(auto_error=False)
app = FastAPI(
    dependencies=[Depends(http_bearer)],
)
app.include_router(auth.router)
app.include_router(tasks.router)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Exception handler for HTTPException in FastAPI applications.

    This function intercepts HTTPException errors and returns a JSONResponse
    with a standardized error format. It ensures that the API provides
    informative error messages to the client.

    Parameters
    ----------
    request : Request
        The incoming HTTP request.
    exc : HTTPException
        The HTTPException raised during request processing.

    Returns
    -------
    JSONResponse
        A response object with a status code and a JSON body containing error details.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": type(exc).__name__,
                "error_message": exc.detail,
            },
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """
    Exception handler for RequestValidationError in FastAPI applications.

    This function handles validation errors raised during request processing,
    returning a JSON response with a standardized error format. It ensures that
    clients receive clear and useful information about validation issues.

    Parameters
    ----------
    request : Request
        The incoming HTTP request.
    exc : RequestValidationError
        The validation error raised during request processing.

    Returns
    -------
    JSONResponse
        A response object with a 422 status code and a JSON body containing error details.
    """
    error_message = exc.errors()[0]
    error_type = error_message.get("type")
    error_msg = error_message.get("msg")
    if exc.body:
        error_message = exc.body
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": error_type,
                "error_message": error_msg,
            },
        ),
    )