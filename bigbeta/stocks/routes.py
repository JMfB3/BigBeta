"""
Stocks Wathlist Routes
"""

from flask import render_template, request, redirect, url_for, Blueprint
from bigbeta import db, bcrypt
from bigbeta.models import Stocks
from bigbeta.stocks.utils import build_watchlist
# from bigbeta.users.forms import RegistrationForm


stocks = Blueprint('stocks', __name__)


@stocks.route("/stocks")
def premarket_gainers():
    """
    Stocks Watchlist Page - One Day Watchlist
    """

    oneday_gainers = build_watchlist(rank_type='1d', wl_cnt=15)

    return render_template('stocks.html', oneday_gainers=oneday_gainers)
