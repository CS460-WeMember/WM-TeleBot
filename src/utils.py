from datetime import datetime


def tryDate(date):
    try:
        return datetime((date % 100) + 2000, (date % 10000) // 100, date // 10000)
    except ValueError:
        return
