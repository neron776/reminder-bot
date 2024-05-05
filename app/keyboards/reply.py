from aiogram.types import ReplyKeyboardRemove, KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Создать напоминалку')],
        [KeyboardButton(text='Мои напоминалки')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Текст в поле сообщения...'
)

set_reminder_date_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Сегодня'), KeyboardButton(text='Ежедневно')],
        [KeyboardButton(text='Отмена')]
    ]
)

reminder_update_date_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Сегодня'), KeyboardButton(text='Ежедневно')],
        [KeyboardButton(text='Оставить без изменений')],
        [KeyboardButton(text='Отмена')]
    ]
)

# добавить через 30 мин и через час:
set_reminder_time_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='08:00'), KeyboardButton(text='12:00')],
        [KeyboardButton(text='18:00'), KeyboardButton(text='21:00')],
        [KeyboardButton(text='Отмена')]
    ]
)

reminder_update_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Оставить без изменений')],
        [KeyboardButton(text='Отмена')]
    ]
)

reminder_update_time_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='08:00'), KeyboardButton(text='12:00')],
        [KeyboardButton(text='18:00'), KeyboardButton(text='21:00')],
        [KeyboardButton(text='Оставить без изменений')],
        [KeyboardButton(text='Отмена')]
    ]
)

reminder_cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Отмена')]
    ],
    resize_keyboard=True
)

del_kb = ReplyKeyboardRemove()


def get_keyboard(*buttons: str, placeholder: str = None, sizes: tuple[int] = (2,)):
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(buttons, start=0):
        keyboard.add(KeyboardButton(text=text))
        keyboard.adjust(*sizes).as_markup()
