import asyncio
from .langchain import pdf_loader, get_chain
from .models import Chat
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.exceptions import SynchronousOnlyOperation


class LangChainConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.vector_store = None
        self.chain = None
        self.chat_id = None

    async def connect(self):
        # Parse chat_id from the URL.
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']

        # Get the chat object from the database.
        chat = await sync_to_async(Chat.objects.get)(id=int(self.chat_id))

        # If, chat is found, create a RAG chain.
        if chat is not None:
            pages = await self.load_pdf(chat.pdf_url)
            self.vector_store, self.chain = await self.get_chain(pages)

        # Accept the connection
        await self.accept()

    async def receive(self, text_data):
        if self.chain is None:
            await self.send(text_data="Invalid chat!")

        input_data = text_data.strip()

        async for chunk in self.chain.astream(input_data):
            await self.send(text_data=chunk)

    async def disconnect(self, close_code):
        if self.vector_store is not None:
            print("Deleting Collection...")
            await sync_to_async(self.vector_store.delete_collection)()

    async def load_pdf(self, pdf_url):
        # Wrap the synchronous pdf_loader function with sync_to_async
        return await sync_to_async(pdf_loader)(pdf_url)

    async def get_chain(self, pages):
        # Wrap the synchronous get_chain function with sync_to_async
        return await sync_to_async(get_chain)(pages)
