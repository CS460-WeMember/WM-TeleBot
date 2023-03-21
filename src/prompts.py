import telegram

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

choice_reminder_day = telegram.ReplyKeyboardMarkup(
    [['Mon', 'Tue', 'Wed'],
     ['Thu', 'Fri', 'Sat'],
     ['Sun']],
    one_time_keyboard=True,
    resize_keyboard=True
)

choice_audio_volume = telegram.ReplyKeyboardMarkup(
    [['Off', 'Quiet'], ['Moderate', 'Loud']],
    one_time_keyboard=True,
    resize_keyboard=True
)

choice_device = telegram.ReplyKeyboardMarkup(
    [['Button 1', 'Button 2'], ['Toothbrush Holder']],
    one_time_keyboard=True,
    resize_keyboard=True
)

choice_color = telegram.ReplyKeyboardMarkup(
    [['Red', 'Orange', 'Yellow'], ['Green', 'Blue', 'Purple'], ['Pink', 'White']],
    one_time_keyboard=True,
    resize_keyboard=True
)

choice_brightness = telegram.ReplyKeyboardMarkup(
    [['Low', 'Med', 'High']],
    one_time_keyboard=True,
    resize_keyboard=True
)

choice_cfm_cam = telegram.ReplyKeyboardMarkup(
    [['Yes', 'No']],
    one_time_keyboard=True,
    resize_keyboard=True
)
