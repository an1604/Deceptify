from flask import Blueprint
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_blueprint(file_manager, socketio):
    from app.Server.data.DataStorage import Data
    from app.main.routes import execute_routes

    logging.info("Initializing main blueprint...")

    main = Blueprint('main', __name__)

    try:
        data_storage = Data().get_data_object()
        logging.info("Data storage object created successfully.")
    except Exception as e:
        logging.error(f"Failed to create data storage object: {e}")
        raise

    try:
        execute_routes(main, data_storage, file_manager, socketio)
        logging.info("Routes executed successfully.")
    except Exception as e:
        logging.error(f"Failed to execute routes: {e}")
        raise

    return main
