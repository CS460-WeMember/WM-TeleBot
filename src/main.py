import logging
import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters

import prompts
import responses
from pocketbaseapi import PocketbaseApi
from utils import tryDate, tryTime, checkReminders

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
    REMINDERDEVICE, REMINDERCFMPHOTO, \
    SETTINGS, TBTIMER = range(16)

pbapi = PocketbaseApi()

user_chat_id_list, ct_chat_id_list = [], []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(text="Hi there, are you the User or Caretaker?",
                                    reply_markup=prompts.choice_user_caretaker)
    context.user_data['user_type'] = update.message.text

    return USERTYPE


async def prompt_user_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'User':
        if update.message.from_user.id not in user_chat_id_list:
            user_chat_id_list.append(update.message.from_user.id)
    else:
        if update.message.from_user.id not in ct_chat_id_list:
            ct_chat_id_list.append(update.message.from_user.id)

    await update.message.reply_text(
        text="What would you like to do?",
        reply_markup=prompts.choice_action_type
    )

    return ACTIONTYPE


async def prompt_action_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # React to action type
    if update.message.text == 'Set Reminder':
        await update.message.reply_text(
            text="Set a reminder title"
        )
        return REMINDERTITLE
    elif update.message.text == 'Check Reminders':
        await update.message.reply_text(
            text=checkReminders(reg_list=pbapi.regular_list, adh_list=pbapi.adhoc_list)
        )

        await update.message.reply_text(
            text="What would you like to do now?",
            reply_markup=prompts.choice_action_type
        )

        return ACTIONTYPE
    elif update.message.text == 'Settings':
        await update.message.reply_text(
            text="Adjust settings like the toothbrush timer!",
            reply_markup=prompts.choice_tbtime
        )

        return TBTIMER

    return responses.parse_action_choice(update.message.text)


async def prompt_reminder_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['title'] = update.message.text
    await update.message.reply_text(
        text="What type of notification?",
        reply_markup=prompts.choice_reminder_freq
    )

    return REMINDERTYPE


async def prompt_reminder_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Once':
        context.user_data["reminder_type"] = 'adhoc'

    elif update.message.text == 'Daily':
        context.user_data["reminder_type"] = 'regular'
        context.user_data['day'] = -1

    elif update.message.text == 'Weekly':
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
    day_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
    context.user_data['day'] = day_map[update.message.text]
    await update.message.reply_text(
        text="When would you like this reminder to be? HHMM"
    )

    return REMINDERWHENTIME


async def prompt_reminder_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Do some verification
    parsed = tryDate(int(update.message.text))
    if parsed is None:
        await update.message.reply_text(
            text="Please enter a validate in format DDMMYY",
        )
        return REMINDERWHENDATE
    else:
        context.user_data['date'] = parsed

    await update.message.reply_text(
        text="When would you like this reminder to be? HHMM"
    )

    return REMINDERWHENTIME


async def prompt_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    res = tryTime(int(update.message.text))
    context.user_data['time'] = res
    context.user_data['hour'] = res.hour
    context.user_data['minute'] = res.minute

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
    vol_map = {'Off': 0, 'Quiet': 33, 'Moderate': 67, 'Loud': 100}
    context.user_data['volume'] = vol_map[update.message.text]

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
    bright_map = {'Low': 33, 'Med': 67, "High": 100}
    context.user_data['brightness'] = bright_map[update.message.text]

    await update.message.reply_text(
        text="What device do you want to link?",
        reply_markup=prompts.choice_device
    )

    return REMINDERDEVICE


async def prompt_device(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    device_map = {"Button 1": 0, "Button 2": 1, "Toothbrush Holder": 'toothbrush'}
    context.user_data['device'] = device_map[update.message.text]

    await update.message.reply_text(
        text="Would you require the confirmation camera??",
        reply_markup=prompts.choice_cfm_cam
    )

    return REMINDERCFMPHOTO


async def prompt_cfm_cam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['confirmation_cam'] = update.message.text.lower()

    await update.message.reply_text(
        text="Thank you, creating reminder"
    )

    if context.user_data['reminder_type'] == 'adhoc':
        data = MultipartEncoder(
            fields={
                'title': str(context.user_data['title']),
                'when': str(datetime.combine(context.user_data['date'], context.user_data['time'])),
                'options': '{"light": "' + str(context.user_data['color']) + '","brightness": "'
                           + str(context.user_data['brightness']) + '","sound": "' + str(context.user_data['volume'])
                           + '","confirmation": "' + str(context.user_data['confirmation_cam']) + '"}',
                'audio': ('sound.oga', requests.get(context.user_data['audio'].file_path).content),
                'picture': ('pic.jpg', requests.get(context.user_data['picture'].file_path).content),
                'device': str(context.user_data['device'])
            }
        )
        response = requests.post(os.getenv("POCKETBASEIP") + 'api/collections/adhoc/records', data=data,
                                 headers={'Content-Type': data.content_type})
        print(response.json())
    else:
        data = MultipartEncoder(
            fields={
                'day': str(context.user_data['day']),
                'hour': str(context.user_data['hour']),
                'minute': str(context.user_data['minute']),
                'title': str(context.user_data['title']),
                'audio': ('sound.oga', requests.get(context.user_data['audio'].file_path).content),
                'picture': ('pic.jpg', requests.get(context.user_data['picture'].file_path).content),
                'options': '{"light": "' + str(context.user_data['color']) + '","brightness": "'
                           + str(context.user_data['brightness']) + '","sound": "' + str(context.user_data['volume'])
                           + '","confirmation": "' + str(context.user_data['confirmation_cam']) + '"}',
            }
        )
        response = requests.post(os.getenv("POCKETBASEIP") + 'api/collections/regular/records', data=data,
                                 headers={'Content-Type': data.content_type})
        print(response.json())

    return ConversationHandler.END


async def prompt_tb_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    do = [int(s) for s in update.message.text.split() if s.isdigit()][0]
    print(do)
    pbapi.update_minutes(do)
    await update.message.reply_text(
        text="Ok, got it!, What would you like to do now?",
        reply_markup=prompts.choice_action_type
    )

    return ACTIONTYPE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    for reg in pbapi.regular_list:
        if (reg.day == -1 or reg.day == now.weekday()) and reg.hour == now.hour and reg.minute == now.minute \
                and now.second < 3:
            for user_id in user_chat_id_list:
                await context.bot.send_message(chat_id=user_id, text="Hello, it's time to: " + reg.title)

    for adh in pbapi.adhoc_list:
        if adh.when <= now < adh.when + timedelta(seconds=3):
            for user_id in user_chat_id_list:
                await context.bot.send_message(chat_id=user_id, text="Hello, it's time to: " + adh.title)


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    job_queue = application.job_queue
    job_queue.run_repeating(send_reminder, 3)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERTYPE: [MessageHandler(filters.Regex("^(User|Caretaker)$"), prompt_user_type)],
            ACTIONTYPE: [
                MessageHandler(filters.Regex("^(Set Reminder|Check Reminders|Settings)$"), prompt_action_type)],

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

            REMINDERCFMPHOTO: [MessageHandler(filters.Regex("^(Yes|No)"), prompt_cfm_cam)],

            TBTIMER: [MessageHandler(filters.Regex("^(Toothbrush [0-9] Mins)$"), prompt_tb_time)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()
