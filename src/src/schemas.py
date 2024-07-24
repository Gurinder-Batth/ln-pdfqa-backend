from ninja import Schema


class UserSchema(Schema):
    id: int
    email: str


class UserCreationResponseSchema(Schema):
    status: str
