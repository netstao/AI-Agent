from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv


load_dotenv()
api_base = os.getenv("OPENAI_API_BASE") 
api_key = os.getenv("OPENAI_API_KEY")
llm = OpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=api_key,
    openai_api_base=api_base
    )
prompt = PromptTemplate.from_template("你是一个起名大师,请模仿示例起3个{county}名字,比如男孩经常被叫做{boy},女孩经常被叫做{girl}")
message = prompt.format(county="中国特色的",boy="狗蛋",girl="翠花")
print(message)
llm.predict(message)