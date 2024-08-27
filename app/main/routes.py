from flask import render_template
from app.Server.data.DataStorage import DataStorage
from app.Server.Util import *
from app.main.attack_routes import attack_generation_routes
from app.main.general_routes import general_routes

load_dotenv()


def error_routes(main):  # Error handlers routes
    @main.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @main.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500


def execute_routes(main, data_storage: DataStorage, files_manager,
                   socketio):  # Function that executes all the routes.
    general_routes(main, data_storage, files_manager, socketio)  # General pages navigation
    attack_generation_routes(main, data_storage, files_manager, socketio)  # Attack generation pages navigation
    error_routes(main)  # Errors pages navigation
