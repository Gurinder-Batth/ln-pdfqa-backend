from django.http import HttpResponseNotFound, StreamingHttpResponse, HttpResponseNotAllowed
from .langchain import pdf_loader, get_chain
from django.views.decorators.csrf import csrf_exempt
from .models import Chat


@csrf_exempt
def invoke_chain(request):
    if request.method == "POST":
        chat_id = int(request.POST.get("chat_id"))
        message = request.POST.get("message")
        chat = Chat.objects.get(id=chat_id)

        if chat is None:
            return HttpResponseNotFound("Chat Not Found")

        pages = pdf_loader(chat.pdf_url)
        vector_store, chain = get_chain(pages)

        async def generator():
            for chunk in chain.astream(message):
                yield chunk

        return StreamingHttpResponse(generator(), content_type="text/event-stream")

    return HttpResponseNotAllowed("POST")
