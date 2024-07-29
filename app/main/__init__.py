from flask import Blueprint

main = Blueprint('main', __name__)


def create_blueprint(app):
    from app.Server.data.DataStorage import Data
    from app.main import routes

    data_storage = Data().get_data_object()
    routes.execute_routes(main, app, data_storage)

    return main
