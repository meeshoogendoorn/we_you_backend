"""Utilities for accounts."""

__all__ = (
    "Groups",
    "is_employer",
    "is_employee",
    "is_management",
    "is_administrator",
)

import enum


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
    return user.group_id == Groups.admin


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
    return (
        user.group_id == Groups.management
        or (allow_admin and user.group_id == Groups.admin)
    )


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
    return (
        user.group_id == Groups.employer
        or (allow_admin and user.group_id == Groups.admin)
    )


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
    return (
        user.group_id == Groups.employee
        or (allow_admin and user.group_id == Groups.admin)
    )
