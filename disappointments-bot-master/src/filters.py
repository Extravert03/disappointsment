from typing import Union

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

import db
from utils import get_user_id


class UserInDBFilter(BoundFilter):
    key = 'user_in_db'

    def __init__(self, *, returning_user: bool = False):
        self._returning_user = returning_user

    async def check(self, message: Message) -> Union[bool, dict]:
        user_telegram_id = get_user_id(message)
        is_user_in_db = user_telegram_id in db.ALL_USER_TELEGRAM_IDS
        if is_user_in_db and self._returning_user:
            user = db.get_user_by_telegram_id(user_telegram_id)
            return {'user': user}
        return is_user_in_db
