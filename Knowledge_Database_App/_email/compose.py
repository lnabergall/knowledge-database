"""
Email composition API

Classes:

    Email
"""

from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from Knowledge_Database_App.storage.select_queries import InputError


BASE_URL = Path("Knowledge_Database_App/_email/").resolve().path


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

    def __init__(self, user_address, user_name, content_name=None,
                 days_remaining=None, edit_text=None, vote_result=None,
                 confirmation_id=None, welcome=False):
        self.recipient_address = user_address
        self.user_name = user_name
        self.message = Message()
        self.message["To"] = self.recipient_address
        if (edit_text is not None and
                days_remaining is None and vote_result is None):
            self._compose_edit_alert(content_name, edit_text)
        elif edit_text is not None and vote_result is None:
            self._compose_vote_reminder(content_name, edit_text, days_remaining)
        elif edit_text is not None:
            self._compose_author_validated_alert(
                content_name, edit_text, vote_result)
        elif vote_result is not None:
            self._compose_edit_validated_alert(content_name, vote_result)
        elif confirmation_id is not None:
            self._compose_confirmation_request(confirmation_id, days_remaining)
        elif welcome:
            self._compose_user_welcome()
        else:
            raise InputError("Invalid arguments!")

    def _compose_edit_alert(self, content_name, edit_text):
        self.message["Subject"] = "New Edit!"   # TEMPORARY
        with open(BASE_URL+"templates/edit_alert.html", "r") as html_file:
            rich_text = html_file.read().format(
                user_name=self.user_name,
                content_name=content_name,
                edit_text=edit_text,
            )
        with open(BASE_URL+"templates/edit_alert_plain.txt", "r") as text_file:
            plain_text = text_file.read().format(
                user_name=self.user_name,
                content_name=content_name,
                edit_text=edit_text,
            )
        texts = MIMEMultipart()
        texts.attach(MIMEText(rich_text, "html"))
        texts.attach(MIMEText(plain_text))
        self.message.attach(texts)

    def _compose_vote_reminder(self, content_name, edit_text, days_remaining):
        self.message["Subject"] = "Remember to vote!"   # TEMPORARY
        with open(BASE_URL+"templates/vote_reminder.html", "r") as html_file:
            rich_text = html_file.read().format(
                user_name=self.user_name,
                content_name=content_name,
                edit_text=edit_text,
                days_remaining=days_remaining,
            )
        with open(BASE_URL+"templates/vote_reminder_plain.txt", "r") as text_file:
            plain_text = text_file.read().format(
                user_name=self.user_name,
                content_name=content_name,
                edit_text=edit_text,
                days_remaining=days_remaining,
            )
        texts = MIMEMultipart()
        texts.attach(MIMEText(rich_text, "html"))
        texts.attach(MIMEText(plain_text))
        self.message.attach(texts)

    def _compose_edit_validated_alert(self, content_name, vote_result):
        if vote_result:
            self.message["Subject"] = "Your edit has been accepted!"  # TEMPORARY
            with open(BASE_URL+"templates/edit_accepted.html", "r") as html_file:
                rich_text = html_file.read().format(
                    user_name=self.user_name,
                    content_name=content_name,
                )
            with open(BASE_URL+"templates/edit_accepted_plain.txt", "r") as text_file:
                plain_text = text_file.read().format(
                    user_name=self.user_name,
                    content_name=content_name,
                )
            texts = MIMEMultipart()
            texts.attach(MIMEText(rich_text, "html"))
            texts.attach(MIMEText(plain_text))
            self.message.attach(texts)
        else:
            # TEMPORARY
            self.message["Subject"] = "There was a problem with your edit..."
            with open(BASE_URL+"templates/edit_rejected.html", "r") as html_file:
                rich_text = html_file.read().format(
                    user_name=self.user_name,
                    content_name=content_name,
                )
            with open(BASE_URL+"templates/edit_rejected_plain.txt", "r") as text_file:
                plain_text = text_file.read().format(
                    user_name=self.user_name,
                    content_name=content_name,
                )
            texts = MIMEMultipart()
            texts.attach(MIMEText(rich_text, "html"))
            texts.attach(MIMEText(plain_text))
            self.message.attach(texts)

    def _compose_author_validated_alert(self, content_name,
                                        edit_text, vote_result):
        if vote_result:
            self.message["Subject"] = "An edit has been accepted!"  # TEMPORARY
            with open(BASE_URL+"templates/author_edit_accepted.html", "r") as html_file:
                rich_text = html_file.read().format(
                    user_name=self.user_name,
                    content_name=content_name,
                    edit_text=edit_text,
                )
            with open(BASE_URL+"templates/author_edit_accepted_plain.txt", "r") as text_file:
                plain_text = text_file.read().format(
                    user_name=self.user_name,
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
            with open(BASE_URL+"templates/author_edit_rejected.html", "r") as html_file:
                rich_text = html_file.read().format(
                    user_name=self.user_name,
                    content_name=content_name,
                    edit_text=edit_text,
                )
            with open(BASE_URL+"templates/author_edit_rejected_plain.txt", "r") as text_file:
                plain_text = text_file.read().format(
                    user_name=self.user_name,
                    content_name=content_name,
                    edit_text=edit_text,
                )
            texts = MIMEMultipart()
            texts.attach(MIMEText(rich_text, "html"))
            texts.attach(MIMEText(plain_text))
            self.message.attach(texts)

    def _compose_confirmation_request(self, confirmation_id, days_remaining):
        self.message["Subject"] = "Please confirm your email!"   # TEMPORARY
        with open(BASE_URL+"templates/email_confirmation.html", "r") as html_file:
            rich_text = html_file.read().format(
                user_name=self.user_name,
                confirmation_id=confirmation_id,
                days_remaining=days_remaining,
            )
        with open(BASE_URL+"templates/email_confirmation_plain.txt", "r") as text_file:
            plain_text = text_file.read().format(
                user_name=self.user_name,
                confirmation_id=confirmation_id,
                days_remaining=days_remaining,
            )
        texts = MIMEMultipart()
        texts.attach(MIMEText(rich_text, "html"))
        texts.attach(MIMEText(plain_text))
        self.message.attach(texts)

    def _compose_user_welcome(self):
        self.message["Subject"] = "You just joined something awesome!"   # TEMPORARY
        with open(BASE_URL+"templates/user_welcome.html", "r") as html_file:
            rich_text = html_file.read().format(
                user_name=self.user_name,
            )
        with open(BASE_URL+"templates/user_welcome_plain.txt", "r") as text_file:
            plain_text = text_file.read().format(
                user_name=self.user_name,
            )
        texts = MIMEMultipart()
        texts.attach(MIMEText(rich_text, "html"))
        texts.attach(MIMEText(plain_text))
        self.message.attach(texts)
