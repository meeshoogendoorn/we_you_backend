"""Utilities for accounts."""

__all__ = (
    "is_employer",
    "is_employee",
    "is_management",
    "is_administrator",
)

from django.db.models.query import Q


def is_administrator(user):
    """
    Check whether the user is a admin or not.

    :param user: The user to check for
    :type user: accounts.models.User

    :return: whether the user is a admin or not.
    :rtype: bool
    """
    return user.groups.filter(id=1).exists()


def is_management(user, allow_admin=True):
    """
    Check whether the user is a manager or not.

    :param user: The user to check for
    :type user: accounts.models.User

    :param allow_admin: Whether to give a false positive when admin or not
    :type allow_admin: bool

    :return: whether the user is a admin or not.
    :rtype: bool
    """
    query = Q(id=2) | Q(id=1) if allow_admin else Q(id=2)
    return user.groups.filter(query).exists()


def is_employer(user, allow_admin=True):
    """
    Check whether the user is a employer or not.

    :param user: The user to check for
    :type user: accounts.models.User

    :param allow_admin: Whether to give a false positive when admin or not
    :type allow_admin: bool

    :return: whether the user is a employer or not.
    :rtype: bool
    """
    query = Q(id=3) | Q(id=1) if allow_admin else Q(id=3)
    return user.groups.filter(query).exists()


def is_employee(user, allow_admin=True):
    """
    Check whether the user is a employee or not.

    :param user: The user to check for
    :type user: accounts.models.User

    :param allow_admin: Whether to give a false positive when admin or not
    :type allow_admin: bool

    :return: whether the user is a employee or not.
    :rtype: bool
    """
    query = Q(id=4) | Q(id=1) if allow_admin else Q(id=4)
    return user.groups.filter(query).exists()
