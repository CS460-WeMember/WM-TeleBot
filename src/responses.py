import main


def parse_action_choice(choice_string):
    if choice_string == 'Set Reminder':
        return main.REMINDERTITLE
    elif choice_string == 'Check Reminders':
        return main.REMINDERCHECK
    elif choice_string == 'Settings':
        return main.SETTINGS


def parse_reminder_type_choice(choice_string):
    if choice_string == 'Once':
        return main.REMINDERWHENDATE
    elif choice_string == 'Daily':
        return main.REMINDERWHENTIME
    elif choice_string == 'Weekly':
        return main.REMINDERWEEKDAY
