"""Utilities for accounts."""

__all__ = (
    "Groups",
    "is_employer",
    "is_employee",
    "is_management",
    "is_administrator",
)

import enum
import functools

from django.db.models.query import Q


class Groups(enum.IntEnum):
    """
    Enumerator to give groups a clearer name.

    Please note that this must be equal to the
    groups.json fixture.
    """

    admin = 1
    management = 2
    employer = 3
    employee = 4


@functools.lru_cache()
def is_administrator(user):
    """
    Check whether the user is a admin or not.

    :param user: The user to check for
    :type user: accounts.models.User

    :return: whether the user is a admin or not.
    :rtype: bool
    """
    return user.groups.filter(id=Groups.admin).exists()


@functools.lru_cache()
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
    query = (
        Q(id=Groups.management) | Q(id=Groups.admin)
        if allow_admin else
        Q(id=Groups.management)
    )
    return user.groups.filter(query).exists()


@functools.lru_cache()
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
    query = (
        Q(id=Groups.employer) | Q(id=Groups.admin)
        if allow_admin else
        Q(id=Groups.employer)
    )
    return user.groups.filter(query).exists()


@functools.lru_cache()
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
    query = (
        Q(id=Groups.employee) | Q(id=Groups.admin)
        if allow_admin else
        Q(id=Groups.employee)
    )
    return user.groups.filter(query).exists()
