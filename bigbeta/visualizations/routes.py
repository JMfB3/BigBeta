"""
Routes for visualizations
"""

from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from bigbeta import db
from bigbeta.visualizations.forms import VisualizationForm
from bigbeta.models import Send


visualizations = Blueprint('visualizations', __name__)

@visualizations.route("/visualizations")
def visualization():
    """
    Route for a Analytics page
    """

    bldr_sends = Send.query.filter_by(user_id=current_user.id, style='boulder').all()
    j = {'v1': 0, 'v2': 0, 'v3': 0, 'v4': 0, 'v5': 0, 'v6': 0, 'v7': 0, 'v8': 0,
         'v9': 0, 'v10': 0, 'v11': 0, 'v12': 0, 'v13': 0, 'v14': 0, 'v15': 0}
    for i in bldr_sends:
        j[i.grade] += 1
    bldr_json = [{'grade': i, 'sends': j[i]} for i in j]

    sprt_sends = Send.query.filter_by(user_id=current_user.id, style='sport').all()
    j = {'5.10a': 0, '5.10b': 0, '5.10c': 0, '5.10d': 0, '5.11a': 0, '5.11b': 0,
         '5.11c': 0, '5.11d': 0, '5.12a': 0, '5.12b': 0, '5.12c': 0, '5.12d': 0,
         '5.13a': 0, '5.13b': 0, '5.13c': 0, '5.13d': 0}
    for i in sprt_sends:
        j[i.grade] += 1
    sprt_json = [{'grade': i, 'sends': j[i]} for i in j]

    return render_template(
        'visualizations.html',
        bldr_json=bldr_json,
        sprt_json=sprt_json)
