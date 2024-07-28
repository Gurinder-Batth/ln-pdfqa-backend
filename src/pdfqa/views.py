from .langchain import pdf_loader, get_chain
from .models import Chat, Message
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async


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
        chat = await sync_to_async(Chat.objects.get)(id=int(self.chat_id))
        self.chat = chat

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
        message = ""

        async for chunk in self.chain.astream(input_data):
            message += chunk
            await self.send(text_data=chunk)

        message_id = 1
        last_message = await sync_to_async(Message.objects.last)()

        if last_message is not None:
            message_id = last_message.id + 1

        await sync_to_async(Message.objects.bulk_create)([
            Message(id=message_id, chat=self.chat, message=input_data, role="user"),
            Message(id=message_id + 1, chat=self.chat, message=message, role="assistant")
        ])

    async def disconnect(self, close_code):
        if self.vector_store is not None:
            print("Deleting Collection...")
            await sync_to_async(self.vector_store.delete_collection)()

        print("Connection dropped!!")

    async def load_pdf(self, pdf_url):
        # Wrap the synchronous pdf_loader function with sync_to_async
        return await sync_to_async(pdf_loader)(pdf_url)

    async def get_chain(self, pages):
        # Wrap the synchronous get_chain function with sync_to_async
        return await sync_to_async(get_chain)(pages)
