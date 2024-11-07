from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
from .routers import tasks, auth

http_bearer = HTTPBearer(auto_error=False)
app = FastAPI(dependencies=[Depends(http_bearer)])
app.include_router(tasks.router)
app.include_router(auth.router)
