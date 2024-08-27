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
    login_url = f"{BASE_URL}/authorize_user"
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        if email == TEST_EMAIL:
            user = get_test_user('1.1.1.1')
            login_user(user)
            return flask_redirect(url_for('main.index'))
        else:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(login_url, json={
                'email': email
            }, headers=headers)
            if response.status_code == 200:
                success = response.json().get('status')
                if success:
                    session['try_to_logged_in'] = True
                    session['user_email'] = email
                    req_id = response.json().get('req_id')
                    return flask_redirect(url_for('auth.two_factor_login', req_id=req_id))
            print("There was a problem with your email address, please try again.")
    return render_template('auth/login.html', form=form)


@auth.route('/two_factor_login', methods=['GET', 'POST'])
def two_factor_login():
    if 'try_to_logged_in' not in session:
        return flask_redirect(url_for('auth.login'))

    validation_url = f"{BASE_URL}/validate_code"
    req_id = request.args.get('req_id')
    form = AuthenticationForm()
    if form.validate_on_submit():
        code = form.code.data
        response = requests.post(validation_url, {
            'req_id': req_id,
            'code': code
        })
        if response.status_code == 200:
            success = response.json().get('status')
            if success:
                user = User(_id=uuid.uuid4(), email=session.pop('user_email'))
                session.permanent = True  # Mark the session as permanent
                login_user(user)
                session.pop('try_to_logged_in', None)
                next = request.args.get('next')
                if next is None or not next.startswith('/'):
                    next = url_for('main.index')
                return flask_redirect(next)
    return render_template('auth/two_factor_login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    session.clear()
    return flask_redirect(url_for('main.index'))
