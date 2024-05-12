from datetime import datetime, timedelta

def get_time():
    correct_time = datetime.now()
    return correct_time.strftime("%H:%M:%S")


def get_date():
    correct_date = datetime.now()
    return correct_date.strftime("%d.%m.%y")


def get_current_time() -> str:
    correct_time = get_time()
    correct_date = get_date()

    return f'{correct_time}, {correct_date}'
