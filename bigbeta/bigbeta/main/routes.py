"""
Main / General things
"""

from flask import render_template, request, redirect, url_for, Blueprint
from bigbeta.models import Post, Send
from bigbeta.users.forms import RegistrationForm


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    """
    Home page
    """

    return redirect(url_for("users.login"))
    # page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    # sends = Send.query.order_by(Send.created_at.desc()).paginate(page=page, per_page=5)
    # return render_template('home.html', posts=posts, sends=sends)


@main.route("/about")
def about():
    return render_template('about.html', title='About')
