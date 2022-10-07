"""
Stocks Wathlist Routes
"""

from flask import render_template, request, redirect, url_for, Blueprint
from bigbeta import db, bcrypt
from bigbeta.models import Stocks
from bigbeta.stocks.utils import build_watchlist
from datetime import datetime
from pytz import timezone


stocks = Blueprint('stocks', __name__)


@stocks.route("/stocks")
def top_gainers():
    """
    Stocks Watchlist Page - One Day Watchlist
    """

    tz = timezone("US/Eastern")
    rn = datetime.now(tz).time()
    mkt_opn = datetime.strptime("08:00:00", "%H:%M:%S").time()
    mkt_cls = datetime.strptime("16:00:00", "%H:%M:%S").time()
    if rn < mkt_opn:
        rank_type = "preMarket"
    elif rn > mkt_opn and rn < mkt_cls:
        rank_type = "1d"
    elif rn > mkt_cls:
        rank_type = "afterMarket"

    oneday_gainers = build_watchlist(rank_type=rank_type)
    run_time_display = rn.strftime("%H:%M:%S")

    return render_template(
        'stocks.html',
        oneday_gainers=oneday_gainers,
        run_time_display=run_time_display,
        rank_type=rank_type)
