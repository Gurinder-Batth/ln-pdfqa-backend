from datetime import datetime
from typing import List

from ninja_extra import Router
from ninja_jwt.authentication import JWTAuth

from .models import Chat
from .schemas import ChatSchemaList, ChatSchemaCreate

router = Router()


@router.get("", auth=JWTAuth(), response=List[ChatSchemaList])
def get_chats(request):
    return Chat.objects.filter(user=request.user)


@router.post("/create", auth=JWTAuth())
def create_chat(request, data: ChatSchemaCreate):
    _id = 1
    last_chat = Chat.objects.last()

    if last_chat is not None:
        _id = last_chat.id + 1

    chat = Chat(**data.dict(), id=_id, user=request.user, created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat())
    chat.save()

    return {"id": _id}
