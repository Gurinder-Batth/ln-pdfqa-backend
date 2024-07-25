from datetime import datetime
from django.http import HttpResponseNotFound, HttpResponse
from typing import List

from ninja_extra import Router
from ninja_jwt.authentication import JWTAuth

from .models import Chat
from .schemas import ChatSchemaList, ChatSchemaCreate
from .langchain import pdf_loader, get_chain

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


@router.get("/{chat_id}", auth=JWTAuth(), response=ChatSchemaList)
def get_chat(request, chat_id: int):
    return Chat.objects.get(id=chat_id, user=request.user)


@router.post("/{chat_id}", auth=JWTAuth())
def invoke_chain(request, response: HttpResponse, chat_id: int):
    message = request.POST["message"]
    chat = Chat.objects.get(id=chat_id, user=request.user)

    if chat is None:
        return HttpResponseNotFound(dict(status="ERROR", detail="Chat Not Found"))

    pages = pdf_loader(chat.pdf_url)
    vector_store, chain = get_chain(pages)

    response['Content-Type'] = "text/event-stream"

    for chunk in chain.stream(message):
        response.write(chunk)
        response.flush()

    return response
