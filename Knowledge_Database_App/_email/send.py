"""
Email sending API.

Exceptions:

    EmailSendError

Functions:

    send_email
"""

from smtplib import (SMTP, SMTPHeloError, SMTPException,
                     SMTPAuthenticationError, SMTPRecipientsRefused,
                     SMTPSenderRefused, SMTPDataError)


class EmailSendError(Exception):
    """Exception to raise for all emailing send errors."""


mail_server = "smtp.gmail.com"
sending_address = "FringePC1013@gmail.com"
password = "Fr1nge1013"


def send_email(email, address):
    """
    Args:
        email: Message object.
        address: String, expects valid email address.
    """
    with SMTP(host=mail_server, port=587) as sender:
        try:
            sender.starttls()
        except (SMTPHeloError, SMTPException) as e:
            raise EmailSendError(str(e))
        try:
            sender.ehlo_or_helo_if_needed()
        except SMTPHeloError as e:
            raise EmailSendError(str(e))
        try:
            sender.login(sending_address, password)
        except SMTPAuthenticationError as e:
            raise EmailSendError(str(e))
        try:
            sender.send_message(
                email,
                from_addr=sending_address,
                to_addrs=address
            )
        except (SMTPRecipientsRefused, SMTPHeloError,
                SMTPSenderRefused, SMTPDataError) as e:
            raise EmailSendError(str(e))
