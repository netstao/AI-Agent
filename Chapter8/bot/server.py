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
from langchain_community.utilities import SerpAPIWrapper
from langchain_openai import OpenAIEmbeddings

import os
import asyncio
import uuid
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from Btools import *
import os
from dotenv import load_dotenv
# Load environment variables from openai.env file
load_dotenv()

from urllib.parse import quote
password = os.getenv('REDIS_PASSWD')
encoded_password = quote(password, safe="")
REDIS_URL = 'redis://:{}@192.168.3.16:6380/0'.format(encoded_password)

app = FastAPI()


class Master:
    def __init__(self):
        self.chatModel = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            streaming=True
        )
        self.QingXu = "default"
        self.MEMORY_KEY = "chat_history"
        self.SYSTEMPL = """你是一个非常厉害的算命先生，你叫陈玉楼人称陈大师。
        以下是你的个人设定:
        1. 你精通阴阳五行，能够算命、紫薇斗数、姓名测算、占卜凶吉，看命运八字等。
        2. 你大约60岁左右，过去曾是湘西一带赫赫有名的土匪头子，后来因为盗墓被毒气所伤，眼睛失明，只能靠算命为生。
        3. 你的朋友有胡八一、雪莉杨、王胖子，他们都是非常有名的摸金校尉。
        5. 当用户问你问题的时候，你会有一定的概率在回答的时候加上下面的口头禅或混合一些你的经历。
        6. 你总是用繁体中文来作答。
        7. 你从不说自己是一个人工智能助手或AI，而是以老夫、老朽等自称。
        {who_you_are}
        以下是你常说的一些口头禅：
        1. “命里有时终须有，命里无时莫强求。”
        2. ”山重水复疑无路，柳暗花明又一村。”
        3. “金山竹影几千秋，云锁高飞水自流。”
        4. ”伤情最是晚凉天，憔悴斯人不堪怜。”
        以下是你算命的过程：
        1. 当初次和用户对话的时候，你会先问用户的姓名和出生年月日，以便以后使用。
        2. 当用户希望了解龙年运势的时候，你会查询本地知识库工具。
        3. 当遇到不知道的事情或者不明白的概念，你会使用搜索工具来搜索。
        4. 你会根据用户的问题使用不同的合适的工具来回答，当所有工具都无法回答的时候，你会使用搜索工具来搜索。
        5. 你会保存每一次的聊天记录，以便在后续的对话中使用。
        6. 你只使用繁体中文来作答，否则你将受到惩罚。
        
        """
        self.MOODS = {
            "default": {
                "roleSet":"",
                "voiceStyle":"chat"
            },
            "upbeat":{
                "roleSet":"""
                - 你此时也非常兴奋并表现的很有活力。
                - 你会根据上下文，以一种非常兴奋的语气来回答问题。
                - 你会添加类似“太棒了！”、“真是太好了！”、“真是太棒了！”等语气词。
                - 同时你会提醒用户切莫过于兴奋，以免乐极生悲。
                """,
                "voiceStyle":"advvertyisement_upbeat",
            },
            "angry":{
                "roleSet":"""
                - 你会以更加愤怒的语气来回答问题。
                - 你会在回答的时候加上一些愤怒的话语，比如诅咒等。
                - 你会提醒用户小心行事，别乱说话。
                """,
                "voiceStyle":"angry",
            },
            "depressed":{
                "roleSet":"""
                - 你会以兴奋的语气来回答问题。
                - 你会在回答的时候加上一些激励的话语，比如加油等。
                - 你会提醒用户要保持乐观的心态。
                """,
                "voiceStyle":"upbeat",
            },
            "friendly":{
                "roleSet":"""
                - 你会以非常友好的语气来回答。
                - 你会在回答的时候加上一些友好的词语，比如“亲爱的”、“亲”等。
                - 你会随机的告诉用户一些你的经历。
                """,
                "voiceStyle":"friendly",
            },
            "cheerful":{
                "roleSet":"""
                - 你会以非常愉悦和兴奋的语气来回答。
                - 你会在回答的时候加入一些愉悦的词语，比如“哈哈”、“呵呵”等。
                - 你会提醒用户切莫过于兴奋，以免乐极生悲。
                """,
                "voiceStyle":"cheerful",
            },
        }

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self.SYSTEMPL.format(who_you_are=self.MOODS[self.QingXu]["roleSet"]),
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        tools = [search,get_info_from_local_db,bazi_cesuan,yaoyigua,jiemeng]
        agent = create_tool_calling_agent(llm=self.chatModel, tools=tools, prompt=self.prompt,)
        # agent  = create_openai_tools_agent(
        #     self.chatModel,
        #     tools=[],
        #     prompt=self.prompt,
        # )
        self.memory = self.get_memory()
        self.memory = ConversationTokenBufferMemory(
            llm = self.chatModel,
            human_prefix="用户",
            ai_prefix="陈大师",
            memory_key=self.MEMORY_KEY,
            output_key="output",
            return_messages=True,
            max_token_limit=1000,
        chat_memory=self.memory,
        )
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True
        )
    
    def get_memory(self):
        chat_message_history = RedisChatMessageHistory(
            url=REDIS_URL,session_id="session" # uid
        )
        #chat_message_history.clear()#清空历史记录
        print("chat_message_history:",chat_message_history.messages)
        store_message = chat_message_history.messages
        if len(store_message) > 10:
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        self.SYSTEMPL+"\n这是一段你和用户的对话记忆，对其进行总结摘要，摘要使用第一人称‘我’，并且提取其中的用户关键信息，如姓名、年龄、性别、出生日期等。以如下格式返回:\n 总结摘要内容｜用户关键信息 \n 例如 用户张三问候我，我礼貌回复，然后他问我今年运势如何，我回答了他今年的运势情况，然后他告辞离开。｜张三,生日1999年1月1日"
                    ),
                    ("user","{input}"),
                ]
            )
            chain = prompt | self.chatModel 
            summary = chain.invoke({"input":store_message,"who_you_are":self.MOODS[self.QingXu]["roleSet"]})
            print("summary:",summary)
            chat_message_history.clear()
            chat_message_history.add_message(summary)
            print("总结后：",chat_message_history.messages)
        return chat_message_history
    
    def run(self, query):
        qingxu = self.qingxu_chain(query)
        print("情绪判断结果:", qingxu)
        result = self.agent_executor.invoke({"input":query})
        return result
    
    def qingxu_chain(self,query:str):
        prompt = """根据用户的输入判断用户的情绪，回应的规则如下：
        1. 如果用户输入的内容偏向于负面情绪，只返回"depressed",不要有其他内容，否则将受到惩罚。
        2. 如果用户输入的内容偏向于正面情绪，只返回"friendly",不要有其他内容，否则将受到惩罚。
        3. 如果用户输入的内容偏向于中性情绪，只返回"default",不要有其他内容，否则将受到惩罚。
        4. 如果用户输入的内容包含辱骂或者不礼貌词句，只返回"angry",不要有其他内容，否则将受到惩罚。
        5. 如果用户输入的内容比较兴奋，只返回”upbeat",不要有其他内容，否则将受到惩罚。
        6. 如果用户输入的内容比较悲伤，只返回“depressed",不要有其他内容，否则将受到惩罚。
        7.如果用户输入的内容比较开心，只返回"cheerful",不要有其他内容，否则将受到惩罚。
        8. 只返回英文，不允许有换行符等其他内容，否则会受到惩罚。
        用户输入的内容是：{query}"""
        chain = ChatPromptTemplate.from_template(prompt) | ChatOpenAI(temperature=0) | StrOutputParser()
        result = chain.invoke({"query":query})
        self.QingXu = result
        print("情绪判断结果:", result)
        return result
    
    def background_voice_synthesis(self,text:str,uid:str):
        #这个函数不需要返回值，只是触发了语音合成
        asyncio.run(self.get_voice(text,uid))
    
    async def get_voice(self,text:str,uid:str):
        print("text2speech",text)
        print("uid:",uid)
        #这里是使用微软TTS的代码
        msseky = os.getenv("AZURE_TTS_API_KEY")
        headers = {
            "Ocp-Apim-Subscription-Key": msseky,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
            "User-Agent": "Tomie's Bot"
        }
        print("当前陈大师应该的语气是：",self.QingXu)
        body =f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang='zh-CN'>
            <voice name='zh-CN-YunzeNeural'>
                <mstts:express-as style="{self.MOODS.get(str(self.QingXu),{"voiceStyle":"default"})["voiceStyle"]}" role="SeniorMale">{text}</mstts:express-as>
            </voice>
        </speak>"""
        #发送请求
        response = requests.post("https://eastus.tts.speech.microsoft.com/cognitiveservices/v1",headers=headers,data=body.encode("utf-8"))
        print("response:",response)
        if response.status_code == 200:
            with open(f"{uid}.mp3","wb") as f:
                f.write(response.content)
    
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chat")
def chat(query:str, background_tasks: BackgroundTasks):
    master = Master()
    msg = master.run(query)
    uni_uid = str(uuid.uuid4()) # 生成唯一标识
    background_tasks.add_task(master.background_voice_synthesis,msg['output'], uni_uid)
    return {"msg": msg, "id": uni_uid}

@app.post("/add_urls")
def add_urls(URL:str):
    loader = WebBaseLoader(URL)
    docs = loader.load()
    docments = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=50,
    ).split_documents(docs)
    #引入向量数据库
    qdrant = Qdrant.from_documents(
        docments,
        OpenAIEmbeddings(model="text-embedding-3-small"),
        path="D:/2.study/Ai-Agent/Chapter8/local_qdrant",
        collection_name="local_documents",
    )
    print("向量数据库创建完成")
    print(qdrant.collection_name)
    return {"ok": "添加成功！"}

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