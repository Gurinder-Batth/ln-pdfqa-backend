import os
from typing import List
from decouple import config

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain import hub

# Loading OPENAI Api Key
os.environ["OPENAI_API_KEY"] = config("OPENAI_SECRET_KEY")


def pdf_loader(url: str):
    loader = PyPDFLoader(url, extract_images=False)
    return loader.load_and_split()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_chain(pages: List[Document]):
    vector_store = Chroma.from_documents(pages, OpenAIEmbeddings())
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})

    prompt = hub.pull("rlm/rag-prompt")
    llm = ChatOpenAI(model="gpt-3.5-turbo")

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return vector_store, rag_chain

