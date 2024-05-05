from datetime import datetime, timedelta


class ReadingProcess:
    started = None


def get_time():
    correct_time = datetime.now()  # + timedelta(hours=+3)
    return correct_time.strftime("%H:%M:%S")


def get_date():
    correct_date = datetime.now()  # + timedelta(hours=+3)
    return correct_date.strftime("%d.%m.%y")


def get_current_time() -> str:
    correct_time = get_time()
    correct_date = get_date()

    return f'{correct_time}, {correct_date}'
