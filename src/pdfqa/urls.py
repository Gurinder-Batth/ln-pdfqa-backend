from django.urls import path
from .views import invoke_chain

urlpatterns = [
    path("", invoke_chain, name="invoke_chain")
]
