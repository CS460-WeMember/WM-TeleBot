import logging
import os
import prompts

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

USERTYPE, ACTIONTYPE, REMINDERTITLE, REMINDERWHEN, REMINDERFREQ, REMINDERPHOTO, REMINDERAUDIO, REMINDERSOUND, \
    REMINDERBRIGHTNESS, REMINDERDEVICE, REMINDERCFMPHOTO = range(11)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(text="Hi there, are you the User or Caretaker?",
                                    reply_markup=prompts.choice_user_caretaker)
    print(update.message)
    return USERTYPE


async def prompt_user_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user

    await update.message.reply_text(
        text="Would you like to set a reminder?",
        reply_markup=prompts.choice_set_reminder
    )
    return ACTIONTYPE


async def prompt_action_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        text="Set a reminder title"
    )

    return REMINDERTITLE


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

    application.add_handler(conv_handler)
    application.run_polling()
