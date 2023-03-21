import main


def parse_action_choice(choice_string):
    if choice_string == 'Set Reminder':
        return main.REMINDERTITLE
    elif choice_string == 'Check Reminders':
        return main.REMINDERCHECK
    elif choice_string == 'Settings':
        return main.SETTINGS
