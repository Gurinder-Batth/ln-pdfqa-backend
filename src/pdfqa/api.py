from datetime import datetime
from typing import List

from ninja_extra import Router
from ninja_jwt.authentication import JWTAuth

from .models import Chat, Message
from .schemas import ChatSchemaList, ChatSchemaCreate, MessagesSchemaList

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


@router.get("{chat_id}", auth=JWTAuth(), response=ChatSchemaList)
def get_chat(request, chat_id: int):
    return Chat.objects.get(id=chat_id, user=request.user)


@router.get("{chat_id}/messages", auth=JWTAuth(), response=List[MessagesSchemaList])
def get_messages(request, chat_id: int):
    return Message.objects.filter(chat_id=chat_id)
