from fastapi import Request, Depends, HTTPException, status

from src.entity.models import Role, User
from src.app_users.services_auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        request: Request,
        user: User = Depends(auth_service.get_current_user),
    ):
        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")


access_to_route_am = RoleAccess([Role.admin, Role.moderator])
access_to_route_a = RoleAccess([Role.admin])
access_to_route_m = RoleAccess([Role.moderator])
