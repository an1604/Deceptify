from flask import Blueprint


def create_blueprint(file_manager, socketio):
    from app.Server.data.DataStorage import Data
    from app.main.routes import execute_routes

    main = Blueprint('main', __name__)

    data_storage = Data().get_data_object()
    execute_routes(main, data_storage, file_manager, socketio)

    return main
