from flask import Blueprint, render_template

blueprint = Blueprint('main', __name__)

@blueprint.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404
