from langchain_community.tools import ElevenLabsText2SpeechTool

text_to_speak = "Hello! 你好! Hola! नमस्ते! Bonjour! こんにちは! مرحبا! 안녕하세요! Ciao! Cześć! Привіт! வணக்கம்!"

tts = ElevenLabsText2SpeechTool(
    voice="Bella",
    text_to_speak=text_to_speak,
    verbose=True
)
tts.name