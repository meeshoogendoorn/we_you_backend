"""Environment engine, will parse a piece of content."""

__all__ = (
    "EnvironmentEngine",
)

import re

from django.utils.html import escape


class EnvironmentEngine(object):
    """Environment engine to parse content based on context."""

    def __init__(self, environ, no_html=True):
        """
        Initialize the engine.

        :param environ: The environment to use
        :type environ: communications.models.Environment

        :param no_html: If set we'll escape the html special chars
        :type no_html: bool
        """
        self.environ = environ
        self.pattern = re.compile(r"{([a-zA-Z\s]+?)}")
        self.mapping = dict(self.environ.variables.values_list("name", "attr"))
        self.no_html = no_html

    def __call__(self, content, context):
        """
        Process the actual content.

        :param content: The content to process
        :type content: str

        :param context: A dictionary with the actual value's
        :type context: dict

        :return: The processed content
        :rtype: str
        """
        def callback(match):
            replace = context[self.mapping[match.group(1)]]
            return escape(replace) if self.no_html else replace

        return self.pattern.sub(callback, content)
