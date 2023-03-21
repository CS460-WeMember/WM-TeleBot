import logging
import os
import prompts
import responses
from pocketbaseapi import PocketbaseApi

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, \
    CallbackQueryHandler

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

USERTYPE, ACTIONTYPE, REMINDERTITLE, REMINDERWHENDATE, REMINDERWEEKDAY, REMINDERWHENTIME,\
    REMINDERTYPE, REMINDERPHOTO, \
    REMINDERAUDIO, REMINDERSOUND, REMINDERPIC, \
    REMINDERBRIGHTNESS, REMINDERDEVICE, REMINDERCFMPHOTO, REMINDERCHECK, SETTINGS = range(16)

pbapi = PocketbaseApi()

sessions = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(text="Hi there, are you the User or Caretaker?",
                                    reply_markup=prompts.choice_user_caretaker)
    context.user_data['userType'] = update.message.text
    print(context.user_data['userType'])

    return USERTYPE


async def prompt_action_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        text="What would you like to do??",
        reply_markup=prompts.choice_set_reminder
    )

    return ACTIONTYPE


async def prompt_action_init(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # React to action type
    if update.message.text == 'Set Reminder':
        await update.message.reply_text(
            text="Set a reminder title"
        )
        return REMINDERTITLE
    elif update.message.text == 'Check Reminders':
        return REMINDERCHECK
    elif update.message.text == 'Settings':
        return SETTINGS

    return responses.parse_action_choice(update.message.text)


async def prompt_reminder_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Handle title
    await update.message.reply_text(
        text="What type of notification?",
        reply_markup=prompts.choice_reminder_freq
    )

    return REMINDERTYPE


async def prompt_reminder_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Handle type
    if update.message.text == 'Once':
        # Date entry
        await update.message.reply_text(
            text="Which day? DDMMYY",
        )

        return REMINDERWHENDATE

    elif update.message.text == 'Daily':
        # Set time format
        await update.message.reply_text(
            text="What time? HHMM",
        )
        print("DAILY")

        return REMINDERWHENTIME

    elif update.message.text == 'Weekly':
        await update.message.reply_text(
            text="Which day of the week?",
            reply_markup=prompts.choice_reminder_day
        )

        return REMINDERWEEKDAY


async def prompt_reminder_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Handle date
    print("WEEKDAY", update.message.text)
    await update.message.reply_text(
        text="When would you like this reminder to be? DDDD"
    )

    return REMINDERWHENTIME


async def prompt_reminder_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("ONCE", update.message.text)
    await update.message.reply_text(
        text="When would you like this reminder to be? DDDD"
    )

    return REMINDERWHENTIME


async def prompt_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("TIME", update.message.text)
    await update.message.reply_text(
        text="Upload an image for this reminder!"
    )

    return REMINDERPIC


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
            USERTYPE: [MessageHandler(filters.Regex("^(User|Caretaker)$"), prompt_action_type)],
            ACTIONTYPE: [MessageHandler(filters.Regex("^(Set Reminder|Check Reminders)$"), prompt_action_init)],

            REMINDERTITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, prompt_reminder_title)],
            REMINDERTYPE: [MessageHandler(filters.Regex("^(Once|Daily|Weekly)$"), prompt_reminder_type)],
            REMINDERWHENDATE: [MessageHandler(filters.Regex("^[0-9]{6}$"), prompt_reminder_date)],
            REMINDERWEEKDAY: [MessageHandler(filters.Regex("^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)$"), prompt_reminder_day)],
            REMINDERWHENTIME: [MessageHandler(filters.Regex("^[0-9]{4}$"), prompt_reminder_time)],
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
