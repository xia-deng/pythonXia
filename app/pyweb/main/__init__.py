from flask.blueprints import Blueprint

main = Blueprint('main', __name__)

from app.pyweb.main import views, errors
