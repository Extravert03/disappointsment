from datetime import datetime
from typing import Iterable, TypeAlias

from peewee import (
    PostgresqlDatabase,
    Model,
    CharField,
    BigIntegerField,
    ForeignKeyField,
    IntegrityError,
    DateTimeField,
    DoesNotExist,
    IntegerField,
)

import exceptions
import settings
from exceptions import UserDoesNotExist
from utils import logger

engine = PostgresqlDatabase(
    database=settings.DATABASE.path.strip('/'),
    password=settings.DATABASE.password,
    user=settings.DATABASE.username,
    host=settings.DATABASE.hostname,
    port=settings.DATABASE.port,
    autorollback=True,
)


class BaseModel(Model):
    class Meta:
        database = engine


class User(BaseModel):
    name = CharField(max_length=255)
    telegram_id = BigIntegerField(unique=True)
    points = IntegerField(default=3)


class Disappointment(BaseModel):
    reason = CharField(max_length=255)
    from_user = ForeignKeyField(User, on_delete='CASCADE')
    to_user = ForeignKeyField(User, on_delete='CASCADE')
    created_at = DateTimeField(default=datetime.now)


FromUser = User.alias()
ToUser = User.alias()

UserOrId: TypeAlias = User | int | str


def get_all_disappointments() -> Iterable[Disappointment]:
    return (Disappointment.select(Disappointment, FromUser, ToUser)
            .join(FromUser, on=(Disappointment.from_user == FromUser.id))
            .switch(Disappointment)
            .join(ToUser, on=(Disappointment.to_user == ToUser.id))
            .execute())


def insert_users():
    users_data = (
        ('Dinaiym', 5093311685,),
        ('Eldos', 896678539,),
        ('Rustam', 756995300,),
    )
    for name, telegram_id in users_data:
        try:
            User.create(name=name, telegram_id=telegram_id)
            logger.debug(f'Name: {name} Telegram ID {telegram_id} created.')
        except IntegrityError:
            logger.debug(f'Name: {name} Telegram ID {telegram_id} already exists in DB.')


def create_tables():
    tables = (
        User,
        Disappointment,
    )
    engine.create_tables(tables)
    logger.debug('Tables created')


def add_disappointment(from_user: User, to_user: User, reason: str) -> Disappointment:
    return Disappointment.create(
        from_user=from_user,
        to_user=to_user,
        reason=reason,
    )


def get_user_by_telegram_id(telegram_id: int) -> User:
    try:
        return User.get(telegram_id=telegram_id)
    except DoesNotExist:
        raise UserDoesNotExist


def get_all_users() -> Iterable[User]:
    return User.select().execute()


def get_user_by_id(user_id: int) -> User:
    try:
        return User.get_by_id(user_id)
    except DoesNotExist:
        raise UserDoesNotExist


def reset_user_points():
    User.update(points=settings.POINTS_AMOUNT).execute()


def get_user_disappointments_amount(user: User) -> int:
    return Disappointment.select().where(Disappointment.to_user == user).count()


def get_disappointment_by_id(disappointment_id: int | str) -> Disappointment:
    try:
        return (Disappointment.select(Disappointment, FromUser, ToUser)
                .join(FromUser, on=(Disappointment.from_user == FromUser.id))
                .switch(Disappointment)
                .join(ToUser, on=(Disappointment.to_user == ToUser.id))
                .where(Disappointment.id == disappointment_id)
                .get())
    except DoesNotExist:
        raise exceptions.DisappointmentDoesNotExist


def delete_disappointment_by_id(pk: int | str) -> int:
    return Disappointment.delete_by_id(pk)


def get_disappointments_from_user_by_telegram_id(
        telegram_id: int | str,
) -> Iterable[Disappointment]:
    return (Disappointment.select(Disappointment, FromUser, ToUser)
            .join(FromUser, on=(Disappointment.from_user == FromUser.id))
            .switch(Disappointment)
            .join(ToUser, on=(Disappointment.to_user == ToUser.id))
            .where(FromUser.telegram_id == telegram_id)
            .order_by(Disappointment.created_at.asc())
            .execute())


ALL_USER_TELEGRAM_IDS = set()

if not ALL_USER_TELEGRAM_IDS:
    users = get_all_users()
    ALL_USER_TELEGRAM_IDS |= {user.telegram_id for user in users}
    logger.debug('User telegram ids cached')
