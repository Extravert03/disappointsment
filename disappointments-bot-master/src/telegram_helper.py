import contextlib

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.exceptions import TelegramAPIError

import db
from bot import bot
from keyboards import ViewDisappointmentButton


async def notify_new_disappointment(user: db.User, disappointment_id: int):
    with contextlib.suppress(TelegramAPIError):
        await bot.send_message(
            chat_id=user.telegram_id,
            text='⚡️ You got new disappointment',
            reply_markup=InlineKeyboardMarkup().add(ViewDisappointmentButton(disappointment_id)),
        )


async def notify_deleted_disappointment(disappointment: db.Disappointment):
    text = (f'Disappointment from user *{disappointment.from_user.name}*'
            f' with reason _{disappointment.reason}_ has been deleted')
    with contextlib.suppress(TelegramAPIError):
        await bot.send_message(
            chat_id=disappointment.to_user.telegram_id,
            text=text
        )
