from flask import Blueprint

main = Blueprint('main', __name__)

from app.main import routes
from app.Server.data.DataStorage import Data

routes.execute_routes(main, Data().get_data_object())
