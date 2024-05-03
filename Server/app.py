from flask import Flask

app = Flask(__name__)  # The application as an object, Now can use this object to route and staff.


@app.route('/')  # The root router (welcome page).
def index():
    return '<h1>Hello World!</h1>'


@app.route('/newchat')  # The new chat route.
def newchat():
    return '<h1>New Chat</h1>'


@app.route('/user/<name>')  # The user-page route.
def user(name):
    return '<h1>Hello %s!</h1>' % name


if __name__ == '__main__':
    app.run(debug=True)  # TODO: Remove the debug=True in production.
