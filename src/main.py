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

USERTYPE, ACTIONTYPE, REMINDERTITLE, REMINDERWHENDATE, REMINDERWEEKDAY, REMINDERWHENTIME, \
    REMINDERTYPE, REMINDERPHOTO, \
    REMINDERAUDIO, REMINDERVOLUME, \
    REMINDERCOLOR, REMINDERBRIGHTNESS, \
    REMINDERDEVICE, REMINDERCFMPHOTO, REMINDERCHECK, SETTINGS = range(16)

pbapi = PocketbaseApi()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(text="Hi there, are you the User or Caretaker?",
                                    reply_markup=prompts.choice_user_caretaker)
    context.user_data['user_type'] = update.message.text

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
    context.user_data['title'] = update.message
    await update.message.reply_text(
        text="What type of notification?",
        reply_markup=prompts.choice_reminder_freq
    )

    return REMINDERTYPE


async def prompt_reminder_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Once':
        context.user_data["reminder_type"] = 'adhoc'
    elif update.message.text == 'Daily' or update.message.text == 'Weekly':
        context.user_data["reminder_type"] = 'regular'
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

        return REMINDERWHENTIME

    elif update.message.text == 'Weekly':
        await update.message.reply_text(
            text="Which day of the week?",
            reply_markup=prompts.choice_reminder_day
        )

        return REMINDERWEEKDAY


async def prompt_reminder_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Handle date
    context.user_data['weekday'] = update.message.text
    await update.message.reply_text(
        text="When would you like this reminder to be? HHMM"
    )

    return REMINDERWHENTIME


async def prompt_reminder_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Do some verification
    context.user_data['date'] = update.message.text
    await update.message.reply_text(
        text="When would you like this reminder to be? HHMM"
    )

    return REMINDERWHENTIME


async def prompt_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['time'] = update.message.text
    await update.message.reply_text(
        text="Upload an image for this reminder!",
    )

    return REMINDERPHOTO


async def prompt_reminder_pic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['picture'] = await update.message.photo[-1].get_file()
    await update.message.reply_text(
        text="Upload some audio for this reminder!"
    )

    return REMINDERAUDIO


async def prompt_reminder_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.audio:
        context.user_data['audio'] = await update.message.audio.get_file()
    elif update.message.voice:
        context.user_data['audio'] = await update.message.voice.get_file()

    await update.message.reply_text(
        text="How loud do you want the audio?",
        reply_markup=prompts.choice_audio_volume
    )

    return REMINDERVOLUME


async def prompt_audio_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['volume'] = update.message.text

    await update.message.reply_text(
        text='What color would you like the lights?',
        reply_markup=prompts.choice_color
    )

    return REMINDERCOLOR


async def prompt_light_color(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    color_map = {'Red': 'FF0000', 'Orange': 'FF8300', 'Yellow': 'FFF000', 'Green': '00FF00', 'Blue': '0046FF',
                 'Purple': 'AA00FF', 'Pink': 'FF00E0', 'White': 'FFFFFF'}
    context.user_data['color'] = color_map[update.message.text]

    await update.message.reply_text(
        text="How bright would you like the lights?",
        reply_markup=prompts.choice_brightness
    )

    return REMINDERBRIGHTNESS


async def prompt_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['brightness'] = update.message.text

    await update.message.reply_text(
        text="What device do you want to link?",
        reply_markup=prompts.choice_device
    )

    return REMINDERDEVICE


async def prompt_device(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['device'] = update.message.text

    await update.message.reply_text(
        text="Would you require the confirmation camera??",
        reply_markup=prompts.choice_cfm_cam
    )

    return REMINDERCFMPHOTO


async def prompt_cfm_cam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['confirmation_cam'] = update.message.text

    await update.message.reply_text(
        text="Thank you, creating reminder"
    )

    print(context.user_data.values())

    return ConversationHandler.END


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
            REMINDERWHENTIME: [
                MessageHandler(filters.Regex("^(2[0-3]|[01]?[0-9])([0-5]?[0-9])$"), prompt_reminder_time)],

            REMINDERPHOTO: [MessageHandler(filters.PHOTO, prompt_reminder_pic)],
            REMINDERAUDIO: [MessageHandler(filters.VOICE | filters.AUDIO, prompt_reminder_audio)],

            REMINDERVOLUME: [MessageHandler(filters.Regex("^(Off|Quiet|Moderate|Loud)$"), prompt_audio_volume)],
            REMINDERCOLOR: [MessageHandler(filters.Regex("^(Red|Orange|Yellow|Green|Blue|Purple|Pink|White)$"),
                                           prompt_light_color)],
            REMINDERBRIGHTNESS: [MessageHandler(filters.Regex("^(Low|Med|High)$"), prompt_brightness)],

            REMINDERDEVICE: [MessageHandler(filters.Regex("^(Button 1|Button 2|Toothbrush Holder)$"), prompt_device)],

            REMINDERCFMPHOTO: [MessageHandler(filters.Regex("^(Yes|No)"), prompt_cfm_cam)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()
