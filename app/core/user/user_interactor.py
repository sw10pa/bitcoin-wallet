from dataclasses import dataclass
from typing import Protocol

from app.core.facade import Response
from app.core.repositories import IFatherRepository, UserInfo


@dataclass
class RegisterUserRequest:
    email: str


@dataclass
class RegisterUserResponse(Response):
    api_key: str


class IUserInteractor(Protocol):
    def register_user(self, request: RegisterUserRequest) -> RegisterUserResponse:
        pass


class UserInteractor:
    def __init__(
        self, user_repository: IFatherRepository
    ):  # TODO change to IUserRepository
        self.user_repository = user_repository

    def register_user(self, request: RegisterUserRequest) -> RegisterUserResponse:
        api_key = "Stephane27"  # TODO generate api_key
        user = UserInfo(email=request.email, api_key=api_key)
        self.user_repository.register_user(user)
        return RegisterUserResponse(api_key=api_key, success=True, message="TODO")
