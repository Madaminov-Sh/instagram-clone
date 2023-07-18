from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from rest_framework import exceptions

import phonenumbers
import re
import threading

from decouple import config
from twilio.rest import Client
    

"""""email_regex = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
phone_regex = re.compile(r'\+\d{1,3}\s?\(\d{1,3}\)\s?\d{1,4}\s?-?\d{1,4}')
username_regex = re.compile(r'^[a-zA-Z0-9_.-]+$')"""""

email_regex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
phone_regex = re.compile(r"(\+[0-9]+\s*)?(\([0-9]+\))?[\s0-9\-]+[0-9]+")
username_regex = re.compile(r"^[a-zA-Z0-9_.-]+$")


def check_email_or_phone(email_or_phone):
    if phone_regex.match(email_or_phone):
        try:
            phone_number = phonenumbers.parse(email_or_phone)
            if phonenumbers.is_valid_number(phone_number):
                return 'phone'
        except phonenumbers.phonenumberutil.NumberParseException:
            pass

        data = {
            "success": False,
            "message": "Telefon raqamingiz noto'g'ri formatda"
        }
        raise exceptions.ValidationError(data)
    elif email_regex.match(email_or_phone):
        return "email"
    else:
        data = {
            "success": False,
            "message": "Email yoki telefon raqamingiz noto'g'ri formatda"
        }
        raise exceptions.ValidationError(data)
    
    
def check_user_type(user_input):
    # number = phonenumbers.parse(user_input)

    if re.fullmatch(email_regex, user_input):
        user_input = 'email'
    elif re.fullmatch(username_regex, user_input):
        user_input = 'username'
    elif re.fullmatch(phone_regex, user_input):
        user_input = 'phone'        
    else:
        data = {
            "success": False,
            "message": "username, phone yoki email noto'g'ri kiritilgan"
        }
        raise exceptions.ValidationError(data)
    return user_input


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )
        if data.get('content_type') == 'html':
            email.content_subtype = 'email'
        EmailThread(email).start()

    
def send_email(email, code):
    html_content = render_to_string(
        "email/authentication/activate_account.html",
        {'code':code}
    )
    Email.send_email(
        {
        "subject": "ro'yxatdan o'tish",
        "to_email": email,
        "body": html_content,
        "content_type": "html",
    }
    )

        
# def send_phone(phone, code):
#     account_sid = config('account_sig')
#     auth_token = config('auth_token')
#     client = Client(account_sid, auth_token)
#     client.messages.create(
#         body=f"sizning raqamingizga yuborilgan instagram tastiqlash ko'di: {code}",
#         from_='+998912017385',
#         to=f'{phone}'
#     )
    