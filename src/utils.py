from datetime import datetime, time


def tryDate(date):
    try:
        return datetime((date % 100) + 2000, (date % 10000) // 100, date // 10000)
    except ValueError:
        return


def tryTime(tim):
    return time(tim//100, tim%100)
