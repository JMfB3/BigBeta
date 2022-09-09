"""
Routes for anything sends related
"""

from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from bigbeta import db
from bigbeta.models import Send
from bigbeta.sends.forms import SendForm


sends = Blueprint('sends', __name__)

@sends.route("/send/new", methods=["GET", "POST"])
@login_required
def new_send():
    """
    Route for new send / creating a send
    """
    form = SendForm()
    boulder_grades = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9',
                      'v10', 'v11', 'v12', 'v13', 'v14', 'v15',]
    sport_grades = ['5.10a', '5.10b', '5.10c', '5.10d', '5.11a', '5.11b',
                    '5.11c', '5.11d', '5.12a', '5.12b', '5.12c', '5.12d',
                    '5.13a', '5.13b', '5.13c', '5.13d',]

    if form.validate_on_submit():
        send = Send(
            title='climb',
            # content=form.content.data,
            grade=form.grade.data,
            style=form.style.data,
            author=current_user
        )
        if (send.style == 'boulder' and send.grade in sport_grades) or (send.style == 'sport' and send.grade in boulder_grades):
            flash("Grade and style don't match.", "danger")
            return redirect(url_for("sends.new_send"))
        db.session.add(send)
        db.session.commit()
        all_sends = Send.query.filter_by(user_id=current_user.id).all()
        flash(f"{send.grade} added!", 'success')
        return redirect(url_for("sends.new_send"))
    return render_template('create_send.html',
                           title='New Send',
                           form=form,
                           legend='New Send'
                          )


@sends.route("/send/<int:send_id>")
def send(send_id):
    """
    Route for a single send
    """
    send = Send.query.get_or_404(send_id)
    return render_template('send.html', title=send.title, send=send)


@sends.route("/send/<int:send_id>/update", methods=["GET", "POST"])
@login_required
def update_send(send_id):
    send = Send.query.get_or_404(send_id)
    if send.author != current_user:
        abort(403)
    form = SendForm()
    if form.validate_on_submit():
        send.title = form.title.data
        send.content = form.content.data
        db.session.commit()
        flash('Send updated!', 'success')
        return redirect(url_for('sends.send', send_id=send_id))
    elif request.method == 'GET':
        form.title.data = send.title
        form.content.data = send.content
    return render_template('create_send.html', title='Update Send',
                           form=form,
                           legend='Update Send')


@sends.route("/send/<int:send_id>/delete", methods=["POST"])
@login_required
def delete_send(send_id):
    send = Send.query.get_or_404(send_id)
    if send.author != current_user:
        abort(403)
    db.session.delete(send)
    db.session.commit()
    flash('Send deleted!', 'success')
    return redirect(url_for('main.home'))
