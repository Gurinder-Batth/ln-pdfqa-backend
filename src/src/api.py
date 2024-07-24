from .schemas import UserSchema, UserCreationResponseSchema

from django.contrib.auth.models import User
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController

api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)


@api.get("/me", auth=JWTAuth(), response=UserSchema)
def me(request):
    return request.user


@api.post("/auth/create-user", response=UserCreationResponseSchema)
def create_user(request):
    username = request.POST.get("username")
    password = request.POST.get("password")

    user = User(username=username)
    user.set_password(password)

    user.save()
    return dict(status="OK")
