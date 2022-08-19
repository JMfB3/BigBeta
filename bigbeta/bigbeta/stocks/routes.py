"""
Stocks Wathlist Routes
"""

from flask import render_template, request, redirect, url_for, Blueprint
from bigbeta import db, bcrypt
from bigbeta.models import Stocks
# from bigbeta.users.forms import RegistrationForm


stocks = Blueprint('stocks', __name__)


@stocks.route("/stocks")
def stock():
    """
    Stocks Watchlist Page - One Day Watchlist
    """

    # tickers = Stocks.query
    # return render_template('stocks.html', title='One Day Watchlist', tickers=tickers)
    return render_template('stocks.html')
