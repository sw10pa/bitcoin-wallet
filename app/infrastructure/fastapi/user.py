from fastapi import APIRouter, Depends

from app.core.facade import BTCWalletService
from app.core.user.user_interactor import RegisterUserRequest, RegisterUserResponse
from app.infrastructure.fastapi.dependables import get_core

user_api = APIRouter()


@user_api.post("/users")
def register_user(
    email: str, core: BTCWalletService = Depends(get_core)
) -> RegisterUserResponse:
    request = RegisterUserRequest(email=email)
    return core.register_user(request)
