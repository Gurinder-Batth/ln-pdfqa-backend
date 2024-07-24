from ninja import Schema


class ChatSchemaList(Schema):
    pdf_name: str
    pdf_url: str
    file_key: str