import flask

blueprint = flask.Blueprint('api', __name__)

@blueprint.route('/')
def index():
    return flask.jsonify(ok=1)

@blueprint.route('/widgets')
def widgets():
    return flask.jsonify(widgets=list(
        flask.current_app.window.proxy.debug_widgets))

@blueprint.route('/widget/<name>')
def widget(name):
    widget = flask.current_app.window.proxy.debug_widgets.get(name)
    if widget is None:
        return flask.abort(404)
    params = { 'name' : widget.name,
               'value' : widget.value,
               'type' : widget.value_type.__name__,
               'min' : widget.value_min,
               'max' : widget.value_max }
    return flask.jsonify(params=params)


@blueprint.route('/widget/<name>/set')
def set_widget_value(name):
    widget = flask.current_app.window.proxy.debug_widgets.get(name)
    if widget is None:
        return flask.abort(404)

    value_str = flask.request.args.get('value')
    if value_str is None:
        return flask.abort(500)

    # Coerce the value.
    if widget.value_type is bool:
        value = bool(int(value_str))
    elif widget.value_type is float:
        value = float(value_str)
    elif widget.value_type is int:
        value = int(value_str)
    else:
        value = value_str
    widget.value = value
    flask.current_app.window.update()

    return flask.jsonify(ok=1)
