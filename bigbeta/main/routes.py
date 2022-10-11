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


@main.route("/about")
def about():
    return render_template('about.html', title='About')
