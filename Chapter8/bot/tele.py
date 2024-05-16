import telebot
import urllib.parse
import requests
import json
import os
import asyncio

from dotenv import load_dotenv
load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_API_KEY'))

@bot.message_handler(commands=['start'])
def start_message(message):
    #bot.reply_to(message, '你好!')
    bot.send_message(message.chat.id, '你好我是陈瞎子，欢迎光临!')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    #bot.reply_to(message, message.text)
    try:
        encoded_text = urllib.parse.quote(message.text)
        response = requests.post('http://localhost:8008/chat?query='+encoded_text,timeout=100)
        if response.status_code == 200:
            aisay = json.loads(response.text)
            if "msg" in aisay:
                bot.reply_to(message, aisay["msg"]["output"])
                audio_path = f"{aisay['id']}.mp3"
                asyncio.run(check_audio(message,audio_path))
            else:
                bot.reply_to(message, "对不起,我不知道怎么回答你")
    except requests.RequestException as e:
        bot.reply_to(message, "对不起,我不知道怎么回答你")

async def check_audio(message,audio_path):
    while True:
        if os.path.exists(audio_path):
            with open(audio_path, 'rb') as f:
                bot.send_audio(message.chat.id, f)
            os.remove(audio_path)
            break
        else:
            print("waiting")
            await asyncio.sleep(1) #使用asyncio.sleep(1)来等待1秒

bot.infinity_polling()