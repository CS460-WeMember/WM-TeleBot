class Regular:
    def __init__(self, reg_id, day, hour, minute, title, picture, audio, device, options, last_activated, last_started, last_finished):
        self.reg_id = reg_id
        self.day = day
        self.hour = hour
        self.minute = minute
        self.title = title
        self.picture = picture
        self.audio = audio
        self.device = device
        self.options = options
        self.last_activated = last_activated
        self.last_started = last_started
        self.last_finished = last_finished

    def __str__(self):
        return 'Regular(reg_id=' + str(self.reg_id) + ' day=' + str(self.day) + ' hour=' + str(self.hour) \
            + ' minute=' + str(self.minute) + ' title=' + str(self.title) + ' picture=' + str(self.picture) \
            + ' audio=' + str(self.audio) + ' device' + str(self.device) + ' options' + str(self.options) \
            + ' last_activated=' + str(self.last_activated) + ' last_started=' + str(self.last_started) \
            + ' last_finished=' + str(self.last_finished) + ')'


class Adhoc:
    def __init__(self, adhoc_id, title, when, picture, options, audio, device, started, activated, finished):
        self.adhoc_id = adhoc_id
        self.title = title
        self.when = when
        self.picture = picture
        self.options = options
        self.audio = audio
        self.device = device
        self.started = started
        self.activated = activated
        self.finished = finished

    def __str__(self):
        return 'Adhoc(adhoc_id=' + str(self.adhoc_id) + ' title=' + str(self.title) + ' when=' + str(
            self.when) + ' picture=' + str(self.picture) + ' options=' + str(self.options) \
            + ' audio=' + str(self.audio) + ' device=' + str(self.device) + ' last_started=' + str(self.started) \
            + ' activated=' + str(self.activated) + ' finished=' + str(self.finished) + ')'


class Config:
    def __init__(self, field, value):
        self.field = field
        self.value = value
