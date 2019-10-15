"""Utilities for the activities app."""

__all__ = (
    "AnswerStyles",
)

import enum


class AnswerStyles(enum.IntEnum):
    """
    Primary key mapping of the stored answer styles.

    These styles define how the frontend should display the input of
    the answer. The following answer styles are supported at this point

      - radio: radio buttons with multiple choice
      - slide: a slider with 'multiple choice'
      - plain: open answer, this isn't currently used only stored
    """
    radio = 1
    slide = 2
    plain = 3
