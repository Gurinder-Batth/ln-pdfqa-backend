from typing import List

from ninja_extra import Router
from ninja_jwt.authentication import JWTAuth

from .models import Chat
from .schemas import ChatSchemaList

router = Router()


@router.get("", auth=JWTAuth(), response=List[ChatSchemaList])
def get_chats(request):
    return Chat.objects.filter(user=request.user)
