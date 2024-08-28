import os
import uuid

import requests
from flask import render_template, url_for, session, request, flash
from flask_login import logout_user, login_user
from . import auth
from app.Server.Forms.general_forms import LoginForm, AuthenticationForm, RegisterForm
from flask import redirect as flask_redirect
from app.Server.data.user import get_test_user, User
from dotenv import load_dotenv
from app.requests_for_remote_server.authorize_user import send_authorize_user_request, send_validate_code_request

load_dotenv()

BASE_URL = os.getenv('SERVER_URL')
TEST_USERNAME = os.getenv('TEST_USERNAME')
TEST_EMAIL = os.getenv('TEST_EMAIL')
TEST_PASSWORD = os.getenv('TEST_PASSWORD')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    register_url = f"{BASE_URL}/register"
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        if not \
                (username in TEST_USERNAME and email in TEST_EMAIL and password in TEST_PASSWORD):
            res = requests.post(register_url, {
                'username': username,
                'email': email,
                'password': password
            })
        else:
            session['its_a_test'] = True
        return flask_redirect(url_for('auth.login'))
    return render_template("auth/register.html", form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        if email == TEST_EMAIL:
            user = get_test_user('1.1.1.1')
            login_user(user)
            return flask_redirect(url_for('main.index'))
        else:
            req_id, status = send_authorize_user_request(email)
            if status == 'success' and req_id is not None:
                session['try_to_logged_in'] = True
                session['user_email'] = email
                session['req_id'] = req_id
                return flask_redirect(url_for('auth.two_factor_login'))
            print("There was a problem with your email address, please try again.")
    return render_template('auth/login.html', form=form)


@auth.route('/two_factor_login', methods=['GET', 'POST'])
def two_factor_login():
    if 'try_to_logged_in' not in session:
        return flask_redirect(url_for('auth.login'))

    req_id = session.get('req_id')
    form = AuthenticationForm()
    if form.validate_on_submit():
        code = form.code.data
        status = send_validate_code_request(req_id=req_id, code=code)

        if status:
            user = User(_id=uuid.uuid4(), email=session.pop('user_email'))
            session.permanent = True
            login_user(user)
            session.pop('try_to_logged_in', None)
            session.pop('req_id', None)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return flask_redirect(next)
        else:
            flash("There was a problem to authenticate you.")
    return render_template('auth/two_factor_login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    session.clear()
    return flask_redirect(url_for('main.index'))
