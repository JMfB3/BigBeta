"""
Stocks Watchlist Routes
"""

import os
import json
from flask import render_template, request, redirect, url_for, Blueprint
from bigbeta import db, bcrypt
from bigbeta.stocks.utils import build_watchlist
from datetime import datetime


stocks = Blueprint('stocks', __name__)


@stocks.route("/stocks")
def top_gainers():
    """
    Stocks Watchlist Page - One Day Watchlist
    """

    cur_wd = os.getcwd()
    print(f"opening {cur_wd}/bigbeta/stocks/current_run/current_data.json")

    with open(f"{cur_wd}/bigbeta/stocks/current_run/current_data.json", "r") as f:
        watchlist = json.load(f)

    with open(f"{cur_wd}/bigbeta/stocks/current_run/last_run.txt", "r") as f:
        run_time_display = f.read()

    return render_template(
        'stocks.html',
        watchlist=watchlist,
        run_time_display=run_time_display
        )
