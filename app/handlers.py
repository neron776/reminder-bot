import time
import asyncio

from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter, or_f
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.orm import orm_add_reminder, orm_get_all_reminders, orm_delete_reminder, orm_update_reminder, \
    orm_get_reminder, orm_get_todays_reminders
from app.keyboards import reply
from app.keyboards.inline import get_callback_buttons
from app.timing import get_time, get_date, ReadingProcess, get_current_time

user_router = Router()
user_router.message.filter()


class AddReminder(StatesGroup):
    text = State()
    date = State()
    time = State()

    reminder_for_update = None


async def reading_db(message: types.message, session: AsyncSession):
    ReadingProcess.started = True

    sent = {}
    while True:
        correct_time = get_time()[:-3]

        for reminder in await orm_get_todays_reminders(session, str(message.from_user.id)):
            if correct_time == f'{reminder.time}':
                if not sent.get(f'{reminder.name}_{reminder.time}'):
                    await message.answer(text=reminder.text)
                    sent.update([(f'{reminder.name}_{reminder.time}', reminder.text)])

        if correct_time == '23:59':
            sent.clear()

        print(f"I'm reading the database... {get_time()}")
        await asyncio.sleep(15)


@user_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    await message.answer(text='Привет, это бот, который поможет вам не забыть о ваших делах.\n\n'
                              'Выберите "Создать напоминалку" и далее вы сможете:\n'
                              '- ввести текст напоминания;\n'
                              '- выбрать, когда бот будет присылать вам это сообщение;\n'
                              '- выбрать время напоминания.',
                         reply_markup=reply.start_kb)

    if not ReadingProcess.started:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(reading_db(message, session))
            print('go...')


@user_router.message(Command('show_time'))
async def show_time_cmd(message: types.Message):
    current_datetime = get_current_time()
    await message.answer(text=current_datetime)


@user_router.message(Command('help'))
async def help_cmd(message: types.Message):
    await message.answer(text='/start - Показать приветствие\n'
                              '/help - Список команд\n'
                              '/show_time - Показать текущее время\n')


@user_router.message(F.text == 'Мои напоминалки')
async def show_reminders(message: types.Message, session: AsyncSession):
    await message.answer(text='Ваши напоминалки:')

    for reminder in await orm_get_all_reminders(session, str(message.from_user.id)):
        current_date = datetime.now().strftime("%d.%m.%y")
        if reminder.date == current_date:
            date = 'Сегодня'
        elif reminder.date == 'everyday':
            date = 'Ежедневно'
        else:
            date = reminder.date

        await message.answer(
            text=f"{reminder.text}\n{date}, {reminder.time}",
            reply_markup=get_callback_buttons(btns={
                'Изменить': f'update_{reminder.id}',
                'Удалить': f'delete_{reminder.id}'
            })
        )


@user_router.message(F.text == 'Мои сегодняшние напоминалки')
async def show_todays_reminders(message: types.Message, session: AsyncSession):
    await message.answer(text='Ваши напоминалки на сегодня:')

    for reminder in await orm_get_todays_reminders(session, str(message.from_user.id)):
        if reminder.date == 'everyday':
            date = 'Ежедневно'
        else:
            date = 'Сегодня'

        await message.answer(
            text=f"{reminder.text}\n{date}, {reminder.time}",
            reply_markup=get_callback_buttons(btns={
                'Изменить': f'update_{reminder.id}',
                'Удалить': f'delete_{reminder.id}'
            })
        )


@user_router.callback_query(StateFilter(None), F.data.startswith('update_'))
async def update_reminder(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    reminder_id = callback.data.split("_")[-1]

    reminder_for_update = await orm_get_reminder(session, int(reminder_id))
    AddReminder.reminder_for_update = reminder_for_update

    await callback.answer()
    await callback.message.answer('Введите новый текст напоминалки', reply_markup=reply.reminder_update_kb)
    await state.set_state(AddReminder.text)


@user_router.callback_query(F.data.startswith('delete_'))
async def delete_reminder(callback: types.CallbackQuery, session: AsyncSession):
    reminder_id = callback.data.split("_")[-1]
    await orm_delete_reminder(session, int(reminder_id))

    await callback.answer('Напоминалка удалена', show_alert=True)
    await callback.message.answer('Напоминалка удалена')


# FSM:
@user_router.message(StateFilter(None), F.text == 'Создать напоминалку')
async def add_reminder_text(message: types.Message, state: FSMContext):
    await state.clear()

    await message.answer(text='Введите текст напоминалки', reply_markup=reply.reminder_cancel_kb)
    await state.set_state(AddReminder.text)


@user_router.message(StateFilter('*'), F.text == 'Отмена')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer('Действия отменены', reply_markup=reply.start_kb)


@user_router.message(AddReminder.text, or_f(F.text, F.text == 'Оставить без изменений'))
async def add_reminder_date(message: types.Message, state: FSMContext):
    if message.text == 'Оставить без изменений':
        await state.update_data(
            name=AddReminder.reminder_for_update.name,
            text=AddReminder.reminder_for_update.text
        )
    else:
        if len(message.text) >= 100:
            await message.answer(text='Длина названия не должна превышать 100 символов.\n Введите заново')
            return

        await state.update_data(
            name=str(message.from_user.id),
            text=message.text
        )

    if AddReminder.reminder_for_update:
        await message.answer(text='Введите новую дату напоминалки в формате ДД.ММ.ГГ '
                                  '(например: "01.01.24").\n', reply_markup=reply.reminder_update_date_kb)
    else:
        await message.answer(text='Введите дату напоминалки в формате ДД.ММ.ГГ '
                                  '(например: "01.01.24").\n',
                             reply_markup=reply.set_reminder_date_kb)
    await state.set_state(AddReminder.date)


@user_router.message(AddReminder.date, or_f(F.text, F.text == 'Оставить без изменений'))
async def add_reminder_time(message: types.Message, state: FSMContext):
    current_date = datetime.now().strftime("%d.%m.%y")
    valid = True
    answers_to_mistakes = [
        'Неправильный формат даты.\nПопробуйте еще раз',
        'Неправильный формат даты.\nПопробуйте снова, у вас точно получится!',
        'Неправильный формат даты.\nПопробуйте снова, (формат ДД.ММ.ГГ)'
    ]

    if message.text == 'Оставить без изменений':
        await state.update_data(date=AddReminder.reminder_for_update.date)
    else:
        if message.text == 'Сегодня':
            await state.update_data(date=current_date)
        elif message.text == 'Ежедневно':
            await state.update_data(date='everyday')
        else:
            try:
                valid_date = time.strptime(message.text, "%d.%m.%y")
                await state.update_data(date=message.text)
            except ValueError:
                print('Invalid date!')
                valid = False

    if AddReminder.reminder_for_update and valid:
        await message.answer(text='Введите новое время напоминалки в формате ЧЧ:ММ '
                                  '(например: "12:00").\n', reply_markup=reply.reminder_update_time_kb)
        await state.set_state(AddReminder.time)

    elif not AddReminder.reminder_for_update and valid:
        await message.answer(text='Введите время напоминалки в формате ЧЧ:ММ '
                                  '(например: "12:00").\n',
                             reply_markup=reply.set_reminder_time_kb)
        await state.set_state(AddReminder.time)

    else:
        await message.answer(text='Неправильный формат даты.\nПопробуйте еще раз', reply_markup=reply.set_reminder_date_kb)
        await state.set_state(AddReminder.date)


@user_router.message(AddReminder.time, or_f(F.text, F.text == 'Оставить без изменений'))
async def confirm_reminder(message: types.Message, state: FSMContext, session: AsyncSession):
    valid = True
    if message.text == 'Оставить без изменений':
        await state.update_data(time=AddReminder.reminder_for_update.time)
    else:
        try:
            valid_time = time.strptime(message.text, "%H:%M")
            await state.update_data(time=message.text)
        except ValueError:
            print('Invalid time!')
            valid = False

    if valid:
        await state.update_data(time=message.text)
        data = await state.get_data()

        try:
            if AddReminder.reminder_for_update:
                await orm_update_reminder(session, AddReminder.reminder_for_update.id, data)
                await message.answer(
                    text=f'{data["text"]}\n'
                         f'{data["date"]}, {data["time"]}\n\nизменено',
                    reply_markup=reply.start_kb
                )
                await state.clear()
            elif not AddReminder.reminder_for_update:
                await orm_add_reminder(session, data)
                await message.answer(
                    text=f'{data["text"]}\n'
                         f'{data["date"]}, {data["time"]}\n\nНапоминание создано!',
                    reply_markup=reply.start_kb
                )
                await state.clear()

            AddReminder.reminder_for_update = None

        except Exception as e:
            await message.answer(
                text='Ошибка создания/изменения напоминания', reply_markup=reply.start_kb
            )
            await state.clear()

    else:
        await message.answer(
            text='Неправильный формат времени.\nПопробуйте еще раз', reply_markup=reply.set_reminder_time_kb
        )
        await state.set_state(AddReminder.time)
