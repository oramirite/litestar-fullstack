"""User Account Controllers."""
from __future__ import annotations

from typing import Annotated

from litestar import Controller, Request, Response, get, post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.security.jwt import OAuth2Login

from app.db.models import User as UserModel  # noqa: TCH001
from app.domain.accounts import urls
from app.domain.accounts.dependencies import provide_roles_service, provide_users_service
from app.domain.accounts.guards import auth, requires_active_user
from app.domain.accounts.schemas import AccountLogin, AccountRegister, User
from app.domain.accounts.services import RoleService, UserService
from app.utils import slugify


class AccessController(Controller):
    """User login and registration."""

    tags = ["Access"]
    dependencies = {"users_service": Provide(provide_users_service), "roles_service": Provide(provide_roles_service)}
    signature_namespace = {
        "UserService": UserService,
        "RoleService": RoleService,
        "OAuth2Login": OAuth2Login,
        "RequestEncodingType": RequestEncodingType,
        "Body": Body,
        "User": User,
    }

    @post(
        operation_id="AccountLogin",
        name="account:login",
        path=urls.ACCOUNT_LOGIN,
        cache=False,
        summary="Login",
        exclude_from_auth=True,
    )
    async def login(
        self,
        users_service: UserService,
        data: Annotated[AccountLogin, Body(title="OAuth2 Login", media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Response[OAuth2Login]:
        """Authenticate a user."""
        user = await users_service.authenticate(data.username, data.password)
        return auth.login(user.email)

    @post(
        operation_id="AccountLogout",
        name="account:logout",
        path=urls.ACCOUNT_LOGOUT,
        cache=False,
        summary="Logout",
        exclude_from_auth=True,
    )
    async def logout(
        self,
        request: Request,
    ) -> None:
        """Account Logout"""
        request.cookies.pop(auth.key, None)
        request.clear_session()

    @post(
        operation_id="AccountRegister",
        name="account:register",
        path=urls.ACCOUNT_REGISTER,
        cache=False,
        summary="Create User",
        description="Register a new account.",
    )
    async def signup(
        self,
        request: Request,
        users_service: UserService,
        roles_service: RoleService,
        data: AccountRegister,
    ) -> User:
        """User Signup."""
        user_data = data.to_dict()
        role_obj = await roles_service.get_one_or_none(slug=slugify(users_service.default_role))
        if role_obj is not None:
            user_data.update({"role_id": role_obj.id})
        user = await users_service.create(user_data)
        request.app.emit(event_id="user_created", user_id=user.id)
        return users_service.to_schema(User, user)

    @get(
        operation_id="AccountProfile",
        name="account:profile",
        path=urls.ACCOUNT_PROFILE,
        guards=[requires_active_user],
        summary="User Profile",
        description="User profile information.",
    )
    async def profile(self, request: Request, current_user: UserModel, users_service: UserService) -> User:
        """User Profile."""
        return users_service.to_schema(User, current_user)
