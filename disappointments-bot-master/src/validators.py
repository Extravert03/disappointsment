import db
import exceptions


def check_user_has_enough_points(user: db.User):
    if user.points <= 0:
        raise exceptions.UserHasNotEnoughPoints
