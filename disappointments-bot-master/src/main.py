from aiogram import executor, Dispatcher

import handlers
import db
from bot import dp
from schedulers import reset_user_points_scheduler


async def on_startup(dispatcher: Dispatcher):
    db.create_tables()
    db.insert_users()
    reset_user_points_scheduler.start()


def main():
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_startup,
    )


if __name__ == '__main__':
    main()
