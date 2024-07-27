from datetime import datetime
from ninja import Schema


class ChatSchemaList(Schema):
    id: int
    pdf_name: str
    pdf_url: str
    file_key: str
    created_at: datetime
    updated_at: datetime


class ChatSchemaCreate(Schema):
    pdf_name: str
    pdf_url: str
    file_key: str
