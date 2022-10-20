"""
Stocks Watchlist Routes
"""

import os
import json
from datetime import datetime

from flask import render_template, request, redirect, url_for, Blueprint
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

    cur_wd = os.getcwd()
    try:
        cuser_id = current_user.id
    except:
        cuser_id = -1
    # Get most recently run file and load into table
    with open(f"{cur_wd}/bigbeta/stocks/current_run/current_data.json", "r") as f:
        watchlist = json.load(f)
    with open(f"{cur_wd}/bigbeta/stocks/current_run/last_run.txt", "r") as f:
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
        with open(f"{cur_wd}/bigbeta/stocks/user_search/{current_user.id}_searches.json", "r") as f:
            updated_search_list = json.load(f)
        updated_search_list.append(search_ticker(search_form.tckr_input.data))
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
