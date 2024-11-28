import pickle
import cloudinary
import cloudinary.uploader
from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status, UploadFile, File
from fastapi_limiter.depends import RateLimiter

from src.entity.models import User
from src.app_users.shemas_user import UserResponse, RequestEmail, ChangePassword
from src.database.db import get_db
from src.app_users.services_auth import auth_service
from src.app_users import repository_users
from src.config.config import conf
from src.app_users.services_cache import get_redis_client
from src.app_users.services_email import send_email_pass


router = APIRouter(prefix="/user", tags=["user"])

cloudinary.config(
    cloud_name=conf.CLOUDINARY_NAME,
    api_key=conf.CLOUDINARY_API_KEY,
    api_secret=conf.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=10))],
)
async def get_current_user(
    file: UploadFile = File(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    public_id = f"web25/{user.email}"
    res = await cloudinary.uploader.upload(
        file.file,
        folder="web25",
        public_id=public_id,
        owerite=True,
    )
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )

    user = await repository_users.update_avatar_url(user.email, res_url, db)
    cache = await get_redis_client()
    await cache.set(user.email, pickle.dumps(user))
    await cache.expire(user.email, 300)
    return user


@router.post("/change_password")
async def change_password(
    body: ChangePassword,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CONTACT NOT FOUND")

    body.password = auth_service.get_password_hash(body.password)
    user = await repository_users.change_password(body, db)
    return user


@router.post("/reset_password")
async def reset_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")

    fake = Faker()
    password = fake.password(
        length=8,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )
    data = ChangePassword(email=body.email, password=password)
    background_tasks.add_task(send_email_pass, user.email, user.username, password)

    data.password = auth_service.get_password_hash(password)
    user = await repository_users.change_password(data, db)
    return user
