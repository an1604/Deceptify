from flask import Blueprint


def create_blueprint(app, file_manager):
    from app.Server.data.DataStorage import Data
    from app.main.routes import execute_routes

    main = Blueprint('main', __name__)

    data_storage = Data().get_data_object()
    execute_routes(main, app, data_storage, file_manager)

    return main
