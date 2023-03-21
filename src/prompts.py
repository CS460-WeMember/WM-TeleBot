import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

choice_user_caretaker = telegram.ReplyKeyboardMarkup(
    [['User', 'Caretaker']],
    one_time_keyboard=True,
    resize_keyboard=True)

choice_set_reminder = telegram.ReplyKeyboardMarkup(
    [['Set Reminder'], ['Check Reminders'], ['Settings']],
    one_time_keyboard=True,
    resize_keyboard=True
)

choice_reminder_freq = telegram.ReplyKeyboardMarkup(
    [['Once'], ['Daily'], ['Weekly']],
    one_time_keyboard=True,
    resize_keyboard=True
)
