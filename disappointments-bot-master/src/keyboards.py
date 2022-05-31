from typing import Iterable

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import db

view_disappointment_cd = CallbackData('view-disappointment', 'disappointment_id')
delete_disappointment_cd = CallbackData('delete-disappointment', 'disappointment_id')


class ViewDisappointmentButton(InlineKeyboardButton):

    def __init__(self, disappointment_id: int, text: str = 'Take a look'):
        super().__init__(
            text=text,
            callback_data=view_disappointment_cd.new(disappointment_id=disappointment_id),
        )


class MainMenuMarkup(ReplyKeyboardMarkup):

    def __init__(self):
        super(MainMenuMarkup, self).__init__(
            resize_keyboard=True,
            keyboard=[
                [
                    KeyboardButton('😺 Profile'),
                    KeyboardButton('😈 All disappointments'),
                ],
                [
                    KeyboardButton('👎 New disappointment'),
                ],
            ]
        )


class UsersListWithIDsMarkup(InlineKeyboardMarkup):

    def __init__(self, users: Iterable[db.User]):
        super().__init__(row_width=1)
        self.add(*(InlineKeyboardButton(user.name, callback_data=user.id) for user in users))


class DownloadAsExcelMarkup(InlineKeyboardMarkup):

    def __init__(self):
        super().__init__(row_width=1)
        self.add(InlineKeyboardButton('💾 Download as excel', callback_data='download-as-excel'))


class UserDisappointmentsMenuMarkup(InlineKeyboardMarkup):

    def __init__(self):
        super().__init__(row_width=2)
        self.add(
            InlineKeyboardButton('From me', callback_data='from-user-disappointments'),
            InlineKeyboardButton('To me', callback_data='to-user-disappointments'),
        )


class ProfileMenuMarkup(InlineKeyboardMarkup):

    def __init__(self):
        super().__init__(row_width=1)
        self.add(InlineKeyboardButton('My disappointments', callback_data='user-disappointments'))


class DisappointmentMenuMarkup(InlineKeyboardMarkup):

    def __init__(self, disappointment_id: int | str):
        super().__init__(row_width=1)
        self.add(
            InlineKeyboardButton(
                text='❌ Delete',
                callback_data=delete_disappointment_cd.new(disappointment_id=disappointment_id)
            ),
        )
