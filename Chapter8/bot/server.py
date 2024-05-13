from fastapi import FastAPI,WebSocket,WebSocketDisconnect,BackgroundTasks
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent,AgentExecutor,tool
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.schema import StrOutputParser
from langchain.memory import ConversationTokenBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate

import os
import asyncio
import uuid
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
# from Mytools import *
import os
from dotenv import load_dotenv
# Load environment variables from openai.env file
load_dotenv()

app = FastAPI()

@tool
def test():
    """test"""
    return "test"


class Master:
    def __init__(self):
        self.chatModel = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            streaming=True
        )
        self.MEMORY_KEY = "chat_history"
        self.SYSTEM_KEY = ""
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个助手",
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        self.memory = ""
        tools = [test]
        agent = create_tool_calling_agent(llm=self.chatModel, tools=tools, prompt=self.prompt,)
        # agent  = create_openai_tools_agent(
        #     self.chatModel,
        #     tools=[],
        #     prompt=self.prompt,
        # )
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    def run(self, query):
        result = self.agent_executor.invoke({"input":query})
        return result
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chat")
def chat(query:str):
    master = Master()
    return master.run(query)

@app.post("/add_urls")
def add_urls():
    return {"Hello": "add_urls"}

@app.post("/add_pdfs")
def add_pdfs():
    return {"Hello": "add_pdfs"}

@app.post("/add_texts")
def add_texts():
    return {"Hello": "add_texts"}


@app.post("/add_images")
def add_images():
    return {"Hello": "add_images"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print("WebSocket Disconnected")
        await websocket.close()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8008)