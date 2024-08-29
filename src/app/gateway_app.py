import contextlib 
#import asyncio
#from uuid import uuid4
#from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi_users.exceptions import UserAlreadyExists
from contextlib import asynccontextmanager
from user_db import User, create_db_and_tables, get_async_session, get_user_db
from user_schemas import UserCreate, UserRead, UserUpdate
from users import auth_backend, current_active_user, fastapi_users, get_user_manager
from pydantic import BaseModel
import uvicorn
import logging
import httpx
from typing import List
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis

### USEFUL LINKS ###
    # https://github.com/fastapi-users/fastapi-users/discussions/1361#discussioncomment-8661055 -_> Make nice gui and authentification process happen
    # https://fastapi-users.github.io/fastapi-users/10.3/configuration/authentication/transports/bearer/ --> Must define a bearer transport for the endpoints to work?


### Create context managers for creating a super user on startup ####
get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

### Function to create users per direct manipulation of the database ###
async def create_user(email: str, password: str, is_superuser: bool = False):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(
                        UserCreate(
                            email=email, password=password, is_superuser=is_superuser
                        )
                    )
                    print(f"User created {user}")
    except UserAlreadyExists:
        print(f"User {email} already exists")

### Function to check if the current user is a superuser (for protection).
def current_active_superuser(user: User = Depends(current_active_user)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user

##### TO-DOs: ######

#this solution works and doesnt get a warning for depreceated use of @app.on_event("startup"), but is not written as example in the official redis page!
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    await create_user("admin@example.com", "admin", is_superuser=True) #creation of the superuser on startup
    redis = Redis(host='redis', port=6379, decode_responses=True) #redis might lead to bugging and not closing the containers correctly, therefore a try structure is established.
    await FastAPILimiter.init(redis)
    logging.info("Created all initiations for the lifespan in async def lifespan")
    try:
        yield
    finally:
        await redis.close()
        logging.info("Redis connection closed")

app = FastAPI(lifespan=lifespan)

###### AUTHENTICATION ROUTES #########
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"]
)

@app.get("/authenticated-route", tags=["auth"])
async def authenticated_route(user: User = Depends(current_active_user)):
    if user.is_superuser:
        return {"message": f"Hello {user.email}, you are a superuser"}
    else:
        return {"message": f"Hello {user.email}, you are not a superuser"}

# Placeholder for notifications
notifications = []

@app.get("/status")
async def get_status():
    return {"status": 1}


async def send_training_request(dataset: str, model_name: str, model_params: dict =  {"n_jobs": -1}): #model params could be an argument here...
    async with httpx.AsyncClient(timeout=360) as client: #setting the timeout to 360s to give the training endpoint enough time to finish and to avoid the "false" request error.
        try:
            response = await client.post(
                "http://train-api:8001/train",  # Using service name
                json={"dataset": dataset, "model_name": model_name, "model_params": model_params}
            )
            response.raise_for_status()
            logging.info(f"Training request successful for model: {model_name} with dataset: {dataset}")
        except httpx.HTTPStatusError as exc:
            logging.error(f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}")
        except httpx.RequestError as exc:
            logging.error(f"Request error occurred: {exc}")
        except Exception as exc:
            logging.error(f"Unexpected error occurred: {exc}")

@app.post("/train", dependencies=[Depends(RateLimiter(times=5, seconds=60)), Depends(current_active_superuser)])
async def call_training_api(background_tasks: BackgroundTasks, dataset: str = "Ptbdb", model_name: str = "RFC", model_params: dict = {"n_jobs": -1}):
    background_tasks.add_task(send_training_request, dataset, model_name, model_params)
    return {"message": "Training request received, processing in the background."}


class Notification(BaseModel):
    email: str
    message: str
    
@app.post("/notify")
async def call_notification_api(notification: Notification):
    notifications.append(notification.dict())
    return {"status": "notification sent", "notification": notification.dict()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")