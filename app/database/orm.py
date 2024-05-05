from datetime import datetime

from sqlalchemy import select, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Reminder


async def orm_add_reminder(session: AsyncSession, data: dict):

    reminder_object = Reminder(
        name=data['name'],
        text=data['text'],
        date=data['date'],
        time=data['time']
    )
    session.add(reminder_object)
    await session.commit()


async def orm_get_all_reminders(session: AsyncSession, user_id: str):
    query = select(Reminder).where(Reminder.name == user_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_reminder(session: AsyncSession, reminder_id: int):
    query = select(Reminder).where(Reminder.id == reminder_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_reminder(session: AsyncSession, reminder_id: int, data):
    query = update(Reminder).where(Reminder.id == reminder_id).values(
        name=data['name'],
        text=data['text'],
        date=data['date'],
        time=data['time']
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_reminder(session: AsyncSession, reminder_id: int):
    query = delete(Reminder).where(Reminder.id == reminder_id)
    await session.execute(query)
    await session.commit()


async def orm_get_todays_reminders(session: AsyncSession, user_id: str, today=datetime.now().strftime("%d.%m.%y")):
    query = select(Reminder).filter(or_(Reminder.date == today, Reminder.date == 'everyday')).where(Reminder.name == user_id)
    result = await session.execute(query)
    return result.scalars().all()
