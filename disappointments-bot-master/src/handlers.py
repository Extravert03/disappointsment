from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ChatType, CallbackQuery, Update, ChatActions
from aiogram.utils.markdown import html_decoration

import db
import exceptions
import utils
from bot import dp
from excel_report import generate_disappointments_report
from filters import UserInDBFilter
from keyboards import (
    UsersListWithIDsMarkup,
    MainMenuMarkup,
    view_disappointment_cd,
    DownloadAsExcelMarkup,
    UserDisappointmentsMenuMarkup,
    delete_disappointment_cd,
    ProfileMenuMarkup,
    DisappointmentMenuMarkup,
)
from telegram_helper import notify_new_disappointment, notify_deleted_disappointment
from validators import check_user_has_enough_points


class AddDisappointmentStates(StatesGroup):
    user = State()
    reason = State()


@dp.errors_handler(exception=exceptions.DisappointmentDoesNotExist)
async def on_disappointment_does_not_exist_error(update: Update, exception):
    text = 'This disappointment does not exist'
    if update.message is not None:
        await update.message.answer(text)
    elif update.callback_query is not None:
        await update.callback_query.answer(text, show_alert=True)
    return True


@dp.errors_handler(exception=exceptions.UserHasNotEnoughPoints)
async def on_user_has_not_enough_points_error(update: Update, exception):
    text = ('You have no points to add disappointment point.'
            ' They are updated once in 3 hours, so please wait')
    if update.message is not None:
        await update.message.answer(text)
    elif update.callback_query is not None:
        await update.callback_query.message.answer(text)
    return True


@dp.callback_query_handler(Text('from-user-disappointments'), UserInDBFilter(), state='*')
async def on_from_user_disappointments_cb(callback_query: CallbackQuery):
    disappointments = db.get_disappointments_from_user_by_telegram_id(callback_query.from_user.id)
    for disappointments_group in utils.gen_group_items(disappointments, group_by=10):
        lines = ['Disappointments by you:']
        for disappointment in disappointments_group:
            lines += (
                html_decoration.bold(f'To {disappointment.to_user.name}: ') +
                html_decoration.italic(f'{disappointment.reason.capitalize()}'),
                f'/disappointment_{disappointment.id}',
                '',
            )
        text = '\n'.join(lines)
        await callback_query.message.answer(text, parse_mode='html')
    await callback_query.answer()


@dp.callback_query_handler(
    delete_disappointment_cd.filter(),
    UserInDBFilter(),
    state='*',
)
async def on_delete_disappointment_cb(callback_query: CallbackQuery, callback_data: dict):
    disappointment_id = callback_data['disappointment_id']
    disappointment = db.get_disappointment_by_id(disappointment_id)
    disappointment.delete_instance()
    await notify_deleted_disappointment(disappointment)
    await callback_query.answer('Deleted', show_alert=True)
    await callback_query.message.delete()


@dp.callback_query_handler(Text('to-user-disappointments'), UserInDBFilter(), state='*')
async def on_to_user_disappointments_cb(callback_query: CallbackQuery):
    await callback_query.answer('In development', show_alert=True)


@dp.callback_query_handler(Text('download-as-excel'), UserInDBFilter(), state='*')
async def on_download_as_excel_cb(callback_query: CallbackQuery):
    await ChatActions.upload_document()
    disappointments = db.get_all_disappointments()
    report_path = generate_disappointments_report(disappointments)
    with open(report_path, 'rb') as file:
        await callback_query.message.answer_document(file)
    await callback_query.answer()


@dp.callback_query_handler(Text('user-disappointments'), UserInDBFilter(), state='*')
async def on_user_disappointments_menu_cb(callback_query: CallbackQuery):
    text = 'Do you wanna show disappointments that *are from you* or *to you*'
    markup = UserDisappointmentsMenuMarkup()
    await callback_query.message.answer(text, reply_markup=markup)
    await callback_query.answer()


# This handler always must be on top of the message handlers
@dp.message_handler(chat_type=(ChatType.GROUP, ChatType.SUPERGROUP), state='*')
async def on_message_in_group(message: Message):
    await message.answer('This bot is not allowed for using in groups')


@dp.message_handler(Text(startswith='/disappointment_'), UserInDBFilter(), state='*')
async def on_view_exact_disappointment(message: Message):
    disappointment_id = message.text.split('_')[-1]
    disappointment = db.get_disappointment_by_id(disappointment_id)
    markup = DisappointmentMenuMarkup(disappointment_id)
    text = (f'💩 From user: {html_decoration.bold(disappointment.from_user.name)}\n'
            f'😺 To user: {html_decoration.bold(disappointment.to_user.name)}\n'
            f'📅 Created at: {html_decoration.bold(disappointment.created_at.strftime("%H:%M %d.%m.%Y"))}\n'
            f'💬 Reason: {html_decoration.italic(disappointment.reason)}')
    await message.answer(text, reply_markup=markup, parse_mode='html')


@dp.callback_query_handler(UserInDBFilter(), state=AddDisappointmentStates.user)
async def choose_user_for_disappointment(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(user_id=callback_query.data)
    await AddDisappointmentStates.reason.set()
    await callback_query.message.answer('Your reason 👇')
    await callback_query.answer()


@dp.message_handler(UserInDBFilter(), Text('😈 All disappointments'), state='*')
async def on_all_disappointments_command(message: Message):
    markup = DownloadAsExcelMarkup()
    await message.answer('Disappointments', reply_markup=markup)


@dp.message_handler(Text('👎 New disappointment'), UserInDBFilter(returning_user=True), state='*')
async def new_disappointment(message: Message, user: db.User):
    check_user_has_enough_points(user)
    markup = UsersListWithIDsMarkup(db.get_all_users())
    await AddDisappointmentStates.user.set()
    await message.answer('Who do you wanna add disappointment to?', reply_markup=markup)


@dp.message_handler(UserInDBFilter(returning_user=True), state=AddDisappointmentStates.reason)
async def on_disappointment_reason(message: Message, state: FSMContext, user: db.User):
    state_data = await state.get_data()
    user_id = state_data['user_id']
    check_user_has_enough_points(user)
    to_user = db.get_user_by_id(user_id)
    disappointment = db.add_disappointment(from_user=user, to_user=to_user, reason=message.text)
    user.points = user.points - 1
    user.save()
    await notify_new_disappointment(to_user, disappointment.id)
    await message.answer(f'You added new disappointment to user *{to_user.name}*\n'
                         f'Reason: _{disappointment.reason}_')
    await state.finish()


@dp.callback_query_handler(
    view_disappointment_cd.filter(),
    UserInDBFilter(),
    state='*',
)
async def on_view_disappointment_button(callback_query: CallbackQuery, callback_data: dict):
    disappointment_id = callback_data['disappointment_id']
    disappointment = db.get_disappointment_by_id(disappointment_id)
    text = (f'💩 From user: <b>{disappointment.from_user.name}</b>\n'
            f'😺 To user: <b>{disappointment.to_user.name}</b>\n'
            f'📅 Created at: <b>{disappointment.created_at.strftime("%H:%M %d.%m.%Y")}</b>\n'
            f'💬 Reason: <i>{disappointment.reason}</i>')
    await callback_query.message.answer(text, parse_mode='html')
    await callback_query.answer()


@dp.message_handler(Text('😺 Profile'), UserInDBFilter(returning_user=True), state='*')
async def on_profile_command(message: Message, user: db.User):
    text = (f'➖➖➖➖➖➖➖➖➖➖\n'
            f'👤 Name: *{user.name}*\n'
            f'⭐️ Points left: *{user.points}*\n'
            f'👎 Disappointments from other people: *{db.get_user_disappointments_amount(user)}*\n'
            f'➖➖➖➖➖➖➖➖➖➖')
    await message.answer(text, reply_markup=ProfileMenuMarkup())


@dp.message_handler(UserInDBFilter(), state='*')
async def undefined_user(message: Message, state: FSMContext):
    await message.answer('Main menu is always with you ☺️', reply_markup=MainMenuMarkup())
    await state.finish()


@dp.message_handler(state='*')
async def undefined_user(message: Message):
    await message.answer('I don\'t know you')
