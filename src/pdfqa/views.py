from .langchain import pdf_loader, get_chain
from .models import Chat, Message
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import transaction


class LangChainConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.vector_store = None
        self.chain = None
        self.chat_id = None
        self.chat = None

    async def connect(self):
        # Parse chat_id from the URL.
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']

        # Get the chat object from the database.
        self.chat = await self.get_chat(int(self.chat_id))

        # If, chat is found, create a RAG chain.
        if self.chat is not None:
            pages = await self.load_pdf(self.chat.pdf_url)
            self.vector_store, self.chain = await self.get_chain(pages)

        # Accept the connection
        await self.accept()

    async def receive(self, text_data):
        if self.chain is None:
            await self.send(text_data="Invalid chat!")

        input_data = text_data.strip()
        message = ""

        async for chunk in self.chain.astream(input_data):
            message += chunk
            await self.send(text_data=chunk)

        await self.create_messages(input_data, message)

    async def disconnect(self, close_code):
        if self.vector_store is not None:
            print("Deleting Collection...")
            await database_sync_to_async(self.vector_store.delete_collection)()

        print("Connection dropped!!")

    async def load_pdf(self, pdf_url):
        # Wrap the synchronous pdf_loader function with database_sync_to_async
        return await database_sync_to_async(pdf_loader)(pdf_url)

    async def get_chain(self, pages):
        # Wrap the synchronous get_chain function with database_sync_to_async
        return await database_sync_to_async(get_chain)(pages)

    async def get_chat(self, chat_id):
        return await database_sync_to_async(Chat.objects.get)(id=chat_id)

    @database_sync_to_async
    def create_messages(self, input_data, message):
        with transaction.atomic():
            last_message = Message.objects.last()
            message_id = 1 if last_message is None else last_message.id + 1

            Message.objects.bulk_create([
                Message(id=message_id, chat=self.chat, message=input_data, role="user"),
                Message(id=message_id + 1, chat=self.chat, message=message, role="assistant")
            ])