from datetime import datetime, time


def tryDate(date):
    try:
        return datetime((date % 100) + 2000, (date % 10000) // 100, date // 10000)
    except ValueError:
        return None


def tryTime(tim):
    return time(tim // 100, tim % 100)


def checkReminders(reg_list, adh_list) -> str:
    ret = 'Regular: \n'

    day_map = {-1: 'Daily', 0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday'
        , 6: 'Sunday'}
    for reg in reg_list:
        ret += reg.title + " @ " + day_map[reg.day] + " " + str(reg.hour) + "h" + str(reg.minute) + "m\n"

    ret += '\nAdhoc: \n'

    for adh in adh_list:
        ret += adh.title + " @ " + str(adh.when.replace(second=0, microsecond=0)) + "\n"

    return ret
