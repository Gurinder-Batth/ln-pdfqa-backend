from .schemas import UserSchema

from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController

api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)


@api.get("/me", auth=JWTAuth(), response=UserSchema)
def me(request):
    return request.user
