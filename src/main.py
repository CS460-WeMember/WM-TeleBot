import logging
import os
import prompts
import responses
import datetime
from pocketbaseapi import PocketbaseApi

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, JobQueue
from datetime import datetime

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

USERTYPE, ACTIONTYPE, REMINDERTITLE, REMINDERWHEN, REMINDERFREQ, REMINDERPHOTO, REMINDERAUDIO, REMINDERSOUND, \
    REMINDERBRIGHTNESS, REMINDERDEVICE, REMINDERCFMPHOTO, REMINDERCHECK, SETTINGS = range(
        13)

pbapi = PocketbaseApi()

sessions = {}

# initialise the queue and dispatcher
job_queue = JobQueue()
job_queue.set_dispatcher()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(text="Hi there, are you the User or Caretaker?",
                                    reply_markup=prompts.choice_user_caretaker)
    return USERTYPE


async def prompt_user_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['userType'] = update.message.text
    await update.message.reply_text(
        text="What would you like to do??",
        reply_markup=prompts.choice_set_reminder
    )

    return ACTIONTYPE


async def prompt_action_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        text="Set a reminder title"
    )

    return responses.parse_action_choice(update.message.text)


async def prompt_reminder_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        text="When do you want this reminder to be?",
        reply_markup=prompts.choice_reminder_freq
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

# Use this to send the message to the user
async def send_message(context):
    context.bot.send_message(chat_id=CHAT_ID, text="Scheduled message")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERTYPE: [MessageHandler(filters.Regex("^(User|Caretaker)$"), prompt_user_type)],
            ACTIONTYPE: [MessageHandler(filters.Regex("^(Set Reminder|Check Reminders)$"), prompt_action_type)],

            REMINDERTITLE: [MessageHandler(filters.ALL, prompt_reminder_title)]
            # PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            # LOCATION: [
            #     MessageHandler(filters.LOCATION, location),
            #     CommandHandler("skip", skip_location),
            # ],
            # BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # date is stored as datetime.datetime
    # can use this to schedule message into a queue
    # run_once(callback, i.when, data=None, name=None, chat_id=None, user_id=None, job_kwargs=None)
    #  https://docs.python-telegram-bot.org/en/stable/examples.timerbot.html example here
    for i in pbapi.adhoc_list:
        print(i)


    application.add_handler(conv_handler)
    application.run_polling()

# okay this one i don't know where to put
scheduled_time = datetime.strptime("2023-03-21 18:31:48.335000", "%Y-%m-%d %H:%M:%S.%f")
job_queue.run_once(send_message, scheduled_time)

job_queue.start()