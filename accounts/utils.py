from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage



# this is the logic for sending mail to the user that register

def decode_uid(uidb64):
    """
    Decode the UID from base64.

    Args:
        uidb64 (str): The base64 encoded UID.

    Returns:
        str or None: The decoded UID if successful, otherwise None.
    """

    try:
        # this here decodes the primary key of the user
        uid = urlsafe_base64_decode(uidb64).decode()
        return uid
    except (TypeError, ValueError, OverflowError):
        return None



def send_activation_link(request, user, email):
    """
    Send an activation link to the user's email address.

    Args:
        request (HttpRequest): The HTTP request object.
        user (Account): The user object for whom the activation link is being sent.
        email (str): The email address of the user.

    Returns:
        None
    """

    # now for the sending of email
    try:
        current_site = get_current_site(request)
        # since the current site has been obtained, then we move to sending of mail
        mail_subject = 'Please activate your account.'
        context_string = {
            'user':user,
            'domain':current_site,
            # this here encrypts the primary key of the user
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':default_token_generator.make_token(user),

        }

        # this is the message site
        message = render_to_string('accounts/account_verification_email.html', context_string)
        to_email = email
        send_mail = EmailMessage(mail_subject, message, to=[to_email])
        send_mail.send()
    except Exception as e:
        print(e)
        

def send_reset_password_link(request, user, email):
    """
    Send an activation link to the user's email address.

    Args:
        request (HttpRequest): The HTTP request object.
        user (Account): The user object for whom the activation link is being sent.
        email (str): The email address of the user.

    Returns:
        None
    """

    # now for the sending of email
    try:
        current_site = get_current_site(request)
        # since the current site has been obtained, then we move to sending of mail
        mail_subject = "Please reset your account's password"
        context_string = {
            'user':user,
            'domain':current_site,
            # this here encrypts the primary key of the user
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':default_token_generator.make_token(user),

        }

        # this is the message site
        message = render_to_string('accounts/reset_password_link.html', context_string)
        to_email = email
        send_mail = EmailMessage(mail_subject, message, to=[to_email])
        send_mail.send()
    except Exception as e:
        print(e)