import logging
import itertools
from typing import Iterable, Generator, Any

from aiogram.types import Message, CallbackQuery

import settings

LOG_LEVEL = logging.DEBUG if settings.DEBUG else logging.WARNING

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger()


def get_user_id(query: Message | CallbackQuery) -> int:
    return query.from_user.id


def gen_group_items(iterable: Iterable, group_by: int) -> Generator[Any, None, None]:
    """Collect data into non-overlapping fixed-length chunks or blocks"""
    args = [iter(iterable)] * group_by
    return ((i for i in group if i is not None)
            for group in itertools.zip_longest(*args, fillvalue=None))
