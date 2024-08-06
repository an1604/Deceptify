from flask import render_template, url_for, session, request
from flask_login import logout_user, login_user
from . import auth
from app.Server.Forms.general_forms import LoginForm, AuthenticationForm
from flask import redirect as flask_redirect
from .mfa import authenticate, send_email
from ..Server.Util import get_ip_address
from ..Server.data.user import get_user_from_remote


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data

        user_from_mail = get_user_from_remote(email)
        auth_code = authenticate(user_from_mail.otp_code)
        print(f'Your auth code: {auth_code}')
        # send_email(recipient=email, subject="Your 2FA code", body=f"Your 2FA code is {auth_code}")
        session['try_to_logged_in'] = True
        session['code'] = auth_code  # VERY UNSECURED! JUST FOR TESTING
        return flask_redirect(url_for('auth.two_factor_login'))
    return render_template('auth/login.html', form=form)


@auth.route('/two_factor_login', methods=['GET', 'POST'])
def two_factor_login():
    if 'try_to_logged_in' not in session:
        return flask_redirect(url_for('auth.login'))
    form = AuthenticationForm()
    if form.validate_on_submit():
        code = form.code.data
        if code == session['code']:
            user = get_user_from_remote(get_ip_address())
            session.permanent = True  # Mark the session as permanent
            login_user(user)
            session.pop('try_to_logged_in', None)
            session.pop('code', None)
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
