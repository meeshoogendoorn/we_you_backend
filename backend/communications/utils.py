"""Communications utilities."""

__all__ = (
    "MultiMailTransport",
)

from django.conf import settings
from django.core.mail import send_mass_mail

from communications.models import Email


class MultiMailTransport(object):
    """
    Multi mail transport.

    This class should make sending multiple mails
    a lot cleaner but a bit less strait forward.
    """
    __slots__ = ("context", "handler", "pending")

    select = Email.objects.select_email
    sender = settings.DEFAULT_FROM_EMAIL

    def __init__(self, context, environ, company):
        """
        Initialize the transport.

        :param context: The 'base' context to use
        :type context: dict

        :param environ: The environment to use
        :type environ: communications.models.Environment | int

        :param company: The company to select the correct mail
        :type company: companies.models.Company
        """
        self.pending = []
        self.context = context
        self.handler = self.select(environ, company)

    def __call__(self, address, context):
        context = {**self.context, **context}

        subject = self.handler.subject
        content = self.handler.process_content(context)

        self.pending.append((subject, content, self.sender, (address,)))

    def finish(self, iterable=None):
        """
        Finish the transport by actually sending it.

        :param iterable: A iterable that will be looped through if necessary
        :type iterable: iterable

        :return: The number of emails send
        :rtype: int
        """
        if iterable is not None:
            tuple(iterable)

        return send_mass_mail(self.pending)
