import re
from ipaddress import ip_address
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from fastapi import status


origins = ["*"]
allow_credentials = True
allow_methods = ["*"]
allow_headers = ["*"]

banned_ips = [
    ip_address("192.168.1.12"),
    ip_address("192.168.1.13"),
]


user_agent_ban_list = [r"Googlebot"]


class CORSMiddlewareConfig(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        if "*" in origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
        else:
            origin = request.headers.get("Origin")
            if origin in origins:
                response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = str(allow_credentials)
        response.headers["Access-Control-Allow-Methods"] = ", ".join(allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(allow_methods)
        return response


class BanIPsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            ip = ip_address(request.client.host)
        except ValueError:
            ip = None
        if ip in banned_ips:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"}
            )
        response = await call_next(request)
        return response


class UserAgentBanMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        user_agent = request.headers.get("user-agent")
        for ban_pattern in user_agent_ban_list:
            if re.search(ban_pattern, user_agent):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "You are banned"},
                )
        response = await call_next(request)
        return response
