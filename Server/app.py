from flask import Flask, render_template, make_response, session
from flask_bootstrap import Bootstrap

from flask import request  # For handling client's requests.
from flask import redirect as flask_redirect

app = Flask(__name__)  # The application as an object, Now can use this object to route and staff.
bootstrap = Bootstrap(app)


@app.route('/')  # The root router (welcome page).
def index():
    return render_template('index.html')


@app.route('/newchat')  # The new chat route.
def newchat():
    return render_template('newchat.html')


@app.route('/user/<name>')  # The user-page route.
def user(name):
    return '<h1>Hello %s!</h1>' % name

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Error handlers routes
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.errorhandler(Exception)
def exception_handler(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)  # TODO: Remove the debug=True in production.
