"""
Stocks Watchlist Routes
"""

import os
import json
from datetime import datetime
from pytz import timezone

from flask import render_template, request, redirect, url_for, Blueprint, flash
from flask_login import current_user, login_required

from bigbeta import db, bcrypt
from bigbeta.stocks.forms import SearchForm
from bigbeta.stocks.utils import search_ticker, remove_from_watchlist


stocks = Blueprint('stocks', __name__)


@stocks.route("/stocks", methods=["GET", "POST"])
def top_gainers():
    """
    Same as top_gainers, but includes extra features for theta users
    """
    # Get current time to direct to correct page
    tz = timezone("US/Eastern")
    rn = datetime.now(tz).time()
    weekday = datetime.now(tz).weekday()
    pre_mkt_opn = datetime.strptime("04:00:00", "%H:%M:%S").time()
    aft_hrs_cls = datetime.strptime("20:00:00", "%H:%M:%S").time()
    mkt_opn = datetime.strptime("09:30:00", "%H:%M:%S").time()
    mkt_cls = datetime.strptime("16:00:00", "%H:%M:%S").time()
    if weekday >= 5:
        rank_type = "afterMarket"
    elif rn < pre_mkt_opn or rn > mkt_cls:
        rank_type = "afterMarket"
    elif rn < mkt_opn:
        rank_type = "preMarket"
    elif rn > mkt_opn and rn < mkt_cls:
        rank_type = "1d"


    cur_wd = os.getcwd()
    try:
        cuser_id = current_user.id
    except:
        cuser_id = -1
    # Get most recently run file and load into table
    with open(f"{cur_wd}/bigbeta/stocks/current_run/{rank_type}/current_data.json", "r") as f:
        watchlist = json.load(f)
    with open(f"{cur_wd}/bigbeta/stocks/current_run/{rank_type}/last_run.txt", "r") as f:
        run_time_display = f.read()
    # Get all stocks searched. If none, return empty list (resulting in empty table)
    # TODO: At some point should add functionality to clear the list
    try:
        with open(f"{cur_wd}/bigbeta/stocks/user_search/{current_user.id}_searches.json", "r") as f:
            search_list = json.load(f)
    except:
        search_list = []

    # Get search data
    search_form = SearchForm()
    if search_form.validate_on_submit():
        print("running search form")
        # Remove the ticker from the current watchlist.
        #   Then load the file as a list
        #   Then add the updated data of the searched stock to the list
        #   Then write the new list to the user search file, which will be loaded on redirect
        remove_from_watchlist(search_form.tckr_input.data)
        # Load current list
        with open(f"{cur_wd}/bigbeta/stocks/user_search/{current_user.id}_searches.json", "r") as f:
            updated_search_list = json.load(f)
        # Get data on searched ticker and add it to list
        try:
            updated_search_list.append(search_ticker(search_form.tckr_input.data))
        except:
            flash("Ticker not found - Please check spelling", "danger")
        # Save updated list and load the page with it
        with open(f"{cur_wd}/bigbeta/stocks/user_search/{current_user.id}_searches.json", "w") as f:
            json.dump(updated_search_list, f)
        return redirect(url_for("stocks.top_gainers"))

    return render_template(
        'stocks.html',
        watchlist=watchlist,
        run_time_display=run_time_display,
        search_list=search_list,
        search_form=search_form,
        cuser_id=cuser_id
        )


@stocks.route("/stocks/rmfw", methods=["GET", "POST"])
def top_gainers_rm_from_watchlist_redirect():
    """
    Runs the remove from watchlist function, then loads the top_gainers page
    """
    tckr = request.args.get("tckr")
    remove_from_watchlist(tckr)
    return redirect(url_for("stocks.top_gainers"))
