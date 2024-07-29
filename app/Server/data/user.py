import pyotp
from flask_login import UserMixin

from app.Server.Util import get_email_from_ip

"""
This class is for the login and authentication purposes.
In this case, we need to authorize the user to log in, and using this class, we define
some functions that will be helpful for authorization.

Note: This user will be initialized per session! Without keeping the information available
from session to session.
"""


class User(UserMixin):
    def __init__(self, _id, email):
        self.id = _id
        self.email = email
        self.otp_code = pyotp.random_base32()

    @staticmethod
    def get(user_id):
        # Here you should fetch the user data from your data source
        if user_id == 1:  # Replace with your logic
            return User(_id=user_id, email=get_email_from_ip('1.1.1.1'))
        return None


def get_user_from_remote(user_ip):
    email = get_email_from_ip(user_ip)
    # if email == 'admin@example.com':
    #     return User(id='1', username='admin', email=email)
    return User(_id='1', email=email)
