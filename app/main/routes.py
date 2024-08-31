from flask import render_template
from app.Server.data.DataStorage import DataStorage
from app.Server.Util import *
from app.main.attack_routes import attack_generation_routes
from app.main.general_routes import general_routes
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def error_routes(main):  # Error handlers routes
    @main.errorhandler(404)
    def not_found(error):
        logging.warning(f"404 Not Found Error: {error}")
        return render_template("errors/404.html"), 404

    @main.errorhandler(500)
    def internal_error(error):
        logging.error(f"500 Internal Server Error: {error}")
        return render_template("errors/500.html"), 500


def execute_routes(main, data_storage: DataStorage, files_manager, socketio):
    logging.info("Executing general routes...")
    general_routes(main, data_storage, files_manager, socketio)  # General pages navigation
    logging.info("Executing attack generation routes...")
    attack_generation_routes(main, data_storage, files_manager, socketio)  # Attack generation pages navigation
    logging.info("Executing error handling routes...")
    error_routes(main)  # Errors pages navigation
    logging.info("All routes executed successfully.")
