import logging
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters

import prompts
import responses
from pocketbaseapi import PocketbaseApi

data = MultipartEncoder(
    fields={
        'audio': ('sound.oga', requests.get(
            'https://api.telegram.org/file/bot6141320163:AAFQyt5yj0J9tpSTp6l8NjvyBsJNqz2NnQ4/voice/file_47.oga').content),
        'picture': ('pic.jpg', requests.get(
            'https://api.telegram.org/file/bot6141320163:AAFQyt5yj0J9tpSTp6l8NjvyBsJNqz2NnQ4/photos/file_41.jpg').content),
    }
)
response = requests.patch(os.getenv("POCKETBASEIP") + 'api/collections/adhoc/records/rk59irpcirur7e3', data=data,
                        headers={'Content-Type': data.content_type})

print(response)
