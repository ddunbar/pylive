import flask

blueprint = flask.Blueprint('api', __name__)

@blueprint.route('/')
def index():
    return flask.jsonify(ok=1)
