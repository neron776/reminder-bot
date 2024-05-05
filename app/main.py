import asyncio
import os

from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import BotCommandScopeAllPrivateChats, Message, message

from app.middlewares import DataBaseSession

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from database.engine import create_db, drop_db, session_maker
from app.handlers import user_router
from common.commands_list import private

bot = Bot(token=os.getenv('TOKEN'))

dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)

dp.include_routers(user_router)


async def on_startup(bot):
    run_params = False
    if run_params:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    print('The bot has fallen')


async def check_start_message(bot: Bot):
    await bot.send_message(660638311, 'The bot is running')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await create_db()
    # await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())

    loop = asyncio.get_event_loop()
    loop.create_task(check_start_message(bot))

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
