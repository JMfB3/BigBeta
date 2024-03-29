import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from bigbeta import mail
import json


# Keep for dev env
email_sender = os.environ.get('EMAIL_USER')
# Use for prod
if not email_sender:
    with open('/etc/config.json') as config_file:
        config = json.load(config_file)
    email_sender = config.get('EMAIL_USER')


def save_picture(form_picture):
    """
    Saves a profile photo
    """

    random_hex = secrets.token_hex(8)
    _f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=email_sender,
                  recipients=[user.email])
    msg.body = f"""\
To reset your password, visit the following link
{url_for('users.reset_token', token=token, _external=True)}

If yopu did not make this request then simply ignore this email and \
no changes will be made
"""
    mail.send(msg)
