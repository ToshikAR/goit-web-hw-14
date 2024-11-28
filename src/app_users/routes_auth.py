from fastapi import APIRouter, HTTPException, Depends, Response, status, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.app_users import repository_users
from src.app_users.services_email import send_email
from src.app_users.shemas_user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.app_users.services_auth import auth_service
from src.config import messages

router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserSchema,
    bt: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    # ------------ send email notification ---------------------------
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    # ----------------------------------------------------------------
    return new_user


@router.post("/signin", response_model=TokenSchema)
async def signin(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL)
    # ------------ email ---------------------------
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.NOT_CONFIRMED)
    # ----------------------------------------------
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
        )
    await repository_users.visit_user(user, db)
    # Generate JWT
    access_token = await auth_service.create_access_token(
        data={"sub": user.email, "tokеn": "goit_hw12"}
    )
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/signout", response_model=TokenSchema)
async def signout(
    credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    await repository_users.delete_token(user, db)


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# --------------------------- Email ------------------------------------------------------------
@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")

    if user.confirmed:
        return {"message": "Your email is already confirmed"}

    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        if user.confirmed:
            return {"message": "Your email is already confirmed"}

        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.get("/{username}")
async def request_email_open(username: str, response: Response, db: AsyncSession = Depends(get_db)):
    print("--------------------------------")
    print(f"{username} opened an email")
    print("--------------------------------")

    return FileResponse(
        "src/static/open_check.png", media_type="image/png", content_disposition_type="inline"
    )


# ----------------------------------------------------------------------------------------------
