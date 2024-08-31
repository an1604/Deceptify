import os
from flask import render_template, url_for, session, request, flash
from flask_login import logout_user, login_user
from . import auth
from app.Server.Forms.general_forms import LoginForm, AuthenticationForm, RegisterForm
from flask import redirect as flask_redirect
from app.Server.data.user import get_test_user, User
from dotenv import load_dotenv
from app.auth.mfa import authenticate
from app.Server.LLM.llm_chat_tools.send_email import send_email
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = os.getenv('SERVER_URL')
TEST_USERNAME = os.getenv('TEST_USERNAME')
TEST_EMAIL = os.getenv('TEST_EMAIL')
TEST_PASSWORD = os.getenv('TEST_PASSWORD')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        logging.info(f"Login attempt for email: {email}")

        if email == TEST_EMAIL:
            user = get_test_user('1.1.1.1')
            login_user(user)
            logging.info("Test user logged in successfully.")
            return flask_redirect(url_for('main.index'))

        user_from_mail = User(_id='1', email=email)
        auth_code = authenticate(user_from_mail.otp_code)
        logging.info(f"Authentication code generated: {auth_code}")

        send_email(email_receiver=email, email_subject="Your 2FA code", email_body=f"Your 2FA code is {auth_code}",
                   display_name="Deceptify Admin", from_email="DeceptifyAdmin<Do Not Replay>@gmail.com")
        session['try_to_logged_in'] = True
        session['code'] = auth_code  # VERY UNSECURED! JUST FOR TESTING
        logging.info(f"Email sent to {email} with the 2FA code.")
        return flask_redirect(url_for('auth.two_factor_login', email=email))
    return render_template('auth/login.html', form=form)


@auth.route('/two_factor_login', methods=['GET', 'POST'])
def two_factor_login():
    if 'try_to_logged_in' not in session:
        logging.warning("Unauthorized access attempt to two_factor_login route.")
        return flask_redirect(url_for('auth.login'))

    email = request.args.get('email')
    form = AuthenticationForm()
    if form.validate_on_submit():
        code = form.code.data
        if code == session['code']:
            logging.info("Two-factor authentication successful.")
            user = User(_id='1', email=email)
            session.permanent = True
            login_user(user)
            session.pop('try_to_logged_in', None)
            session.pop('code', None)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return flask_redirect(next)
        else:
            logging.warning("Two-factor authentication failed.")
            flash("Invalid authentication code.")
    return render_template('auth/two_factor_login.html', form=form)


@auth.route('/logout')
def logout():
    logging.info("User logged out.")
    logout_user()
    session.clear()
    return flask_redirect(url_for('main.index'))
