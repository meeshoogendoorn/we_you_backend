"""Utilities for accounts."""

__all__ = (
    "is_employer",
    "is_employee",
    "is_administrator",
)


def is_administrator(user):
    """
    Check whether the user is a admin or not.

    :param user: The user to check for
    :type user: accounts.models.User

    :return: whether the user is a admin or not.
    :rtype: bool
    """
    return user.groups.filter(id=1).exists()


def is_employer(user):
    """
    Check whether the user is a employer or not.

    :param user: The user to check for
    :type user: accounts.models.User

    :return: whether the user is a employer or not.
    :rtype: bool
    """
    return user.groups.filter(id=2).exists()


def is_employee(user):
    """
    Check whether the user is a employee or not.

    :param user: The user to check for
    :type user: accounts.models.User

    :return: whether the user is a employee or not.
    :rtype: bool
    """
    return user.groups.filter(id=1).exists()
