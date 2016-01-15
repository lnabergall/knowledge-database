"""
Email composition API

Classes:

    Email
"""

from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from Knowledge_Database_App.storage.select_queries import InputError


class Email:
    """
    Args:
        user_address: String.
        user_name: String.
        content_name: String.
        days_remaining: Integer.
        edit_text: String.
        vote_result: Boolean.
    Attributes:
        recipient_address: String.
        message: Message object. This is the email intended for sending.
    """

    def __init__(self, user_address, user_name, content_name,
                 days_remaining=None, edit_text=None, vote_result=None):
        self.recipient_address = user_address
        self.message = Message()
        self.message["To"] = self.recipient_address
        if edit_text is not None and days_remaining is None and vote_result is None:
            self._compose_edit_alert(user_name, content_name, edit_text)
        elif edit_text is not None and vote_result is None:
            self._compose_vote_reminder(user_name, content_name,
                                       edit_text, days_remaining)
        elif edit_text is not None:
            self._compose_author_validated_alert(user_name, content_name,
                                                 edit_text, vote_result)
        elif vote_result is not None:
            self._compose_edit_validated_alert(user_name,
                                              content_name, vote_result)
        else:
            raise InputError("Invalid arguments!")

    def _compose_edit_alert(self, user_name, content_name, edit_text):
        self.message["Subject"] = "New Edit!"   # TEMPORARY
        with open("templates\edit_alert.html", "r") as html_file:
            rich_text = html_file.read().format(
                user_name=user_name,
                content_name=content_name,
                edit_text=edit_text,
            )
        with open("templates\edit_alert_plain.txt", "r") as text_file:
            plain_text = text_file.read().format(
                user_name=user_name,
                content_name=content_name,
                edit_text=edit_text,
            )
        texts = MIMEMultipart()
        texts.attach(MIMEText(rich_text, "html"))
        texts.attach(MIMEText(plain_text))
        self.message.attach(texts)

    def _compose_vote_reminder(self, user_name, content_name,
                              edit_text, days_remaining):
        self.message["Subject"] = "Remember to vote!"   # TEMPORARY
        with open(r"templates\vote_reminder.html", "r") as html_file:
            rich_text = html_file.read().format(
                user_name=user_name,
                content_name=content_name,
                edit_text=edit_text,
                days_remaining=days_remaining,
            )
        with open(r"templates\vote_reminder_plain.txt", "r") as text_file:
            plain_text = text_file.read().format(
                user_name=user_name,
                content_name=content_name,
                edit_text=edit_text,
                days_remaining=days_remaining,
            )
        texts = MIMEMultipart()
        texts.attach(MIMEText(rich_text, "html"))
        texts.attach(MIMEText(plain_text))
        self.message.attach(texts)

    def _compose_edit_validated_alert(self, user_name,
                                     content_name, vote_result):
        if vote_result:
            self.message["Subject"] = "Your edit has been accepted!"  # TEMPORARY
            with open("templates\edit_accepted.html", "r") as html_file:
                rich_text = html_file.read().format(
                    user_name=user_name,
                    content_name=content_name,
                )
            with open("templates\edit_accepted_plain.txt", "r") as text_file:
                plain_text = text_file.read().format(
                    user_name=user_name,
                    content_name=content_name,
                )
            texts = MIMEMultipart()
            texts.attach(MIMEText(rich_text, "html"))
            texts.attach(MIMEText(plain_text))
            self.message.attach(texts)
        else:
            # TEMPORARY
            self.message["Subject"] = "There was a problem with your edit..."
            with open("templates\edit_rejected.html", "r") as html_file:
                rich_text = html_file.read().format(
                    user_name=user_name,
                    content_name=content_name,
                )
            with open("templates\edit_rejected_plain.txt", "r") as text_file:
                plain_text = text_file.read().format(
                    user_name=user_name,
                    content_name=content_name,
                )
            texts = MIMEMultipart()
            texts.attach(MIMEText(rich_text, "html"))
            texts.attach(MIMEText(plain_text))
            self.message.attach(texts)

    def _compose_author_validated_alert(self, user_name, content_name,
                                        edit_text, vote_result):
        if vote_result:
            self.message["Subject"] = "An edit has been accepted!"  # TEMPORARY
            with open("templates\author_edit_accepted.html", "r") as html_file:
                rich_text = html_file.read().format(
                    user_name=user_name,
                    content_name=content_name,
                    edit_text=edit_text,
                )
            with open("templates\author_edit_accepted_plain.txt", "r") as text_file:
                plain_text = text_file.read().format(
                    user_name=user_name,
                    content_name=content_name,
                    edit_text=edit_text,
                )
            texts = MIMEMultipart()
            texts.attach(MIMEText(rich_text, "html"))
            texts.attach(MIMEText(plain_text))
            self.message.attach(texts)
        else:
            # TEMPORARY
            self.message["Subject"] = "There was a problem with your edit..."
            with open("templates\author_edit_rejected.html", "r") as html_file:
                rich_text = html_file.read().format(
                    user_name=user_name,
                    content_name=content_name,
                    edit_text=edit_text,
                )
            with open("templates\author_edit_rejected_plain.txt", "r") as text_file:
                plain_text = text_file.read().format(
                    user_name=user_name,
                    content_name=content_name,
                    edit_text=edit_text,
                )
            texts = MIMEMultipart()
            texts.attach(MIMEText(rich_text, "html"))
            texts.attach(MIMEText(plain_text))
            self.message.attach(texts)
