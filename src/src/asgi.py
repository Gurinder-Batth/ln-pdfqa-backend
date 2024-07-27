import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

# Import the Django settings
import django
from django.conf import settings
from django.core.asgi import get_asgi_application

# Configure the settings and load the apps
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from pdfqa.views import LangChainConsumer

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter([
        path('invoke_chain/<str:chat_id>', LangChainConsumer.as_asgi()),
    ]),
})
