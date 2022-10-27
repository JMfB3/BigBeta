import os
import json
import sqlite3
from datetime import datetime, date, timedelta
from pytz import timezone
import requests

import pandas as pd
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup as bs
from webull import webull
from flask import current_app
from flask_login import current_user
from flask_mail import Message

# from bigbeta import db
# from bigbeta.models import User
from bigbeta import create_app_context
from bigbeta import mail
from bigbeta.models import User


wb = webull()
cur_wd = os.getcwd()
tz = timezone("US/Eastern")
cur_dt = datetime.strftime(datetime.now(tz), "%Y_%m_%d")
cur_tm = datetime.strftime(datetime.now(tz), "%H_%M")
cur_tm_log = datetime.strftime(datetime.now(tz), "%H:%M:%S")
##########
# Keep for dev env
wb_user = os.environ.get('WB_USER')
wb_pass = os.environ.get('WB_PASS')
email_sender = os.environ.get('EMAIL_USER')
# Use for prod
if not wb_user:
    with open('/etc/config.json') as config_file:
        config = json.load(config_file)
    wb_user = config.get('WB_USER')
if not wb_pass:
    with open('/etc/config.json') as config_file:
        config = json.load(config_file)
    wb_pass = config.get('WB_PASS')
if not email_sender:
    with open('/etc/config.json') as config_file:
        config = json.load(config_file)
    email_sender = config.get('EMAIL_USER')
wb.login(username=wb_user, password=wb_pass)
########## End login block

print('EMAIL SENDER: ', email_sender)
# Set app context
bigbeta_app = create_app_context()


def build_watchlist(wl_cnt=15, dir="gainer"):
    """
    Builds a watchlist with my fave data points. Customize by premarket, 5 min, etc
    Rank Types: preMarket / afterMarket / 5min / 1d / 5d / 1m / 3m / 52w
    """

    # Determine which watchlist to build (premarket, 1d, afterhours)
    tz = timezone("US/Eastern")
    rn = datetime.now(tz).time()
    mkt_opn = datetime.strptime("09:30:00", "%H:%M:%S").time()
    mkt_cls = datetime.strptime("16:00:00", "%H:%M:%S").time()
    if rn < mkt_opn:
        rank_type = "preMarket"
    elif rn > mkt_opn and rn < mkt_cls:
        rank_type = "1d"
    elif rn > mkt_cls:
        rank_type = "afterMarket"

    # Ping WeBull
    l_watchlist = []
    premkt_gnrs = wb.active_gainer_loser(direction=dir, rank_type=rank_type, count=wl_cnt)
    ### Must dig into list within list
    l_tickers = [r["ticker"]["symbol"] for r in premkt_gnrs["data"]]
    for ticker in l_tickers:
        ticker_dct = fundamentals(ticker)
        #### Add to full DF to be reported at end of processing
        l_watchlist.append(ticker_dct)

    # Write data out to file for storage
    with open(f"{cur_wd}/bigbeta/stocks/history/dt_{cur_dt}__tm__{cur_tm}.json", "w") as f:
        json.dump(l_watchlist, f)
    # Write it out again to an overwritten file for easy retrieval
    with open(f"{cur_wd}/bigbeta/stocks/current_run/current_data.json", "w") as f:
        json.dump(l_watchlist, f)
    # Writes out time of last run
    with open(f"{cur_wd}/bigbeta/stocks/current_run/last_run.txt", "w") as f:
        f.write(f"{rank_type} at {cur_tm_log} EST")

    return l_watchlist


def search_ticker(tckr):
    """
    Search a single ticker
    """

    # Get up-to-date data on the stock
    ticker_dct = fundamentals(tckr.upper())

    return ticker_dct


def remove_from_watchlist(tckr_to_rm):
    """
    Removes a ticker from the current user's watchlist
    """

    try:
        with open(f"{cur_wd}/bigbeta/stocks/user_search/{current_user.id}_searches.json", "r") as f:
            search_list = json.load(f)
    except:
        search_list = []

    overwrite_list = []
    for tckr in search_list:
        if not tckr_to_rm.upper() == tckr['ticker'].upper():
            overwrite_list.append(tckr)

    with open(f"{cur_wd}/bigbeta/stocks/user_search/{current_user.id}_searches.json", "w") as f:
        json.dump(overwrite_list, f)

    return overwrite_list


def get_stock(ticker):
    l = []
    f = fundamentals(ticker)
    l.append(f)
    fdf = pd.DataFrame(l)
    return fdf

def fundamentals(ticker):
    # Gets main data points about a selected ticker
        qts = wb.get_quote(stock=ticker)
        # Retrieve basic data
        try:
            avg_vol = qts['avgVol3M']
        except KeyError:
            avg_vol = 0
        try:
            vol = qts['volume']
        except KeyError:
            vol = 0
        try:
            fff = qts['outstandingShares']
        except KeyError:
            fff = 0
        try:
            cnm = qts['name']
        except KeyError:
            cnm = 0
        try:
            open_price = qts['open']
        except KeyError:
            open_price = 0
        try:
            last_price = qts['pPrice']
        except KeyError:
            last_price = 0
        # Manipulate as needed
        ### Free float
        ffs = round((int(fff) / 1000000), 2)
        ### RVOL
        try:
            rvol = round(int(vol) / int(avg_vol), 2)
        except ZeroDivisionError:
            rvol = 0
        # avg_vol display
        if int(avg_vol) > 1000000:
            avs = round((int(avg_vol) / 1000000), 2)
            display_avg_vol = f"{str(avs)}M"
        else:
            avs = round((int(avg_vol) / 1000), 2)
            display_avg_vol = f"{str(avs)}K"

        # Get SI data
        sis = wb.get_short_interest(stock=ticker)
        # Loop through return dict, set var to last value (no need for prior mos)
        if sis:
            si_ = sis[0]['shortInterst']
            dtc = round(float(sis[0]['daysToCover']), 2)
            si_raw = si_
            si_pct = round(((int(si_) / int(fff)) * 100), 2) if fff != 0 else 0
        else:
            mw_data = get_mktwatch_data(tckr=ticker)
            si_raw = mw_data['si_raw']
            dtc = mw_data['dtc']
            si_pct = mw_data['si_pct']

        # Get number of relevant news stories
        #   Maybe add top story to the final DF
        news_stories = get_news(ticker, cnm)

        # Create a grade for the stock
        grade = 0
        # dicts for grades
        rvol_grades = [1, 2, 5, 10]
        ff_grades = [50, 25, 10, 2.5]
        si_grades = [10, 20, 50, 100]
        dtc_grades = [1, 2.5, 5, 7.5, 10]
        news_grades = [0, 1]
        # Set default grades
        rvol_grade = 0
        ff_grade = 0
        si_grade = 0
        dtc_grade = 0
        news_grade = 0
        # Set grades
        for grade in rvol_grades:
            rvol_grade += (1 / len(rvol_grades)) if rvol >= grade else 0
        for grade in ff_grades:
            ff_grade += (1 / len(ff_grades)) if ffs <= grade else 0
        for grade in si_grades:
            si_grade += (1 / len(si_grades)) if si_pct >= grade else 0
        for grade in dtc_grades:
            dtc_grade += (1 / len(dtc_grades)) if dtc >= grade else 0
        for grade in news_grades:
            news_grade += (1 / len(news_grades)) if news_stories > grade else 0

        stock_grade = round((rvol_grade + ff_grade + si_grade + dtc_grade + news_grade), 2) * 2

        ticker_dct = {
            'ticker': ticker,
            'name': cnm,
            'rvol': rvol,
            'rvol_grade': rvol_grade,
            'avg_vol': int(avg_vol),
            'display_avg_vol': display_avg_vol,
            'display_free_float': f"{str(ffs)}M",
            'free_float': ffs,
            'ff_grade': ff_grade,
            'display_short_interest': f"{str(si_pct)}%",
            'short_interest': si_pct,
            'si_grade': si_grade,
            'display_si_raw': "{:,}".format(int(si_raw)),
            'si_raw': si_raw,
            'dtc': dtc,
            'dtc_grade': dtc_grade,
            'stories': news_stories,
            'news_grade': news_grade,
            'stock_grade': stock_grade,
            'last_price': last_price,
            'date_added': datetime.strftime(datetime.now(tz), "%m/%d/%Y")
            }

        return ticker_dct


def get_news(tckr, company):
    """
    Get number of news stories where ticker is in headline
    """

    matches = 0
    # Get all news stories
    stories_l = wb.get_news(stock=tckr)
    # Loop through story titles. If good name match, count it as a story
    for story in stories_l:
        title = story['title']
        news_date = datetime.strptime(story["newsTime"][:10], "%Y-%m-%d").date()
        # Use fuzz to get a max match score
        tckr_match_score = fuzz.partial_ratio(tckr.lower(), title.lower())
        cpny_match_score = fuzz.partial_ratio(company.lower(), title.lower())
        match_score = max(tckr_match_score, cpny_match_score)
        if match_score > 74 and news_date >= date.today() - timedelta(days=5):
            matches += 1

    if matches > 1:
        return_val = matches
    else:
        return_val = matches

    return return_val


def get_mktwatch_data(tckr):
    url = f'https://fintel.io/ss/us/{tckr}'
    page = requests.get(url)
    soup = bs(page.content, 'html.parser')
    tds = soup.find_all("td")

    headr = ""
    si_raw = 0
    si_pct = 0
    dtc = 0

    for i in tds[:30]:
        # Get the actual data based on the header, which is obtained in the second
        #   part of this loop
        if headr == "Short Interest":
            try:
                si_raw = int(i.contents[0].
                    replace("\n", "").
                    replace(" shares- ", "").
                    replace(",", ""))
            except:
                si_raw = 0
            headr = ""
        # days to cover
        elif headr == "Short Interest Ratio":
            try:
                dtc = float(i.contents[0].replace(" Days to Cover", ""))
            except:
                dtc = 0
            headr = ""
        elif headr == "Short Interest % Float":
            # String maniuplation
            try:
                si_pct = float(i.contents[0].
                replace("\n", "").
                replace("%- ", ""))
            except:
                si_pct = 0
            headr = ""

        # Get the header - The next iteration should contain the data you want
        if i.contents == ["Short Interest"]:
            headr = "Short Interest"
        elif i.contents == ["Short Interest Ratio"]:
            headr = "Short Interest Ratio"
        elif i.contents == ["Short Interest % Float"]:
            headr = "Short Interest % Float"

    return ({'dtc': dtc, 'si_raw': si_raw, 'si_pct': si_pct})


def analyze_watchlist():
    """
    Analyzes the most recent run of build_watchlist to check for anything with outrageous stats.
    If new stocks are found, send an email notification
    Args: None
    Returns: None
    """

    # Open current watchlist, create new list finding stocks with >100% short interest
    with open(f"{cur_wd}/bigbeta/stocks/current_run/current_data.json", "r") as f:
        watchlist = json.load(f)
    outrageous_stocks = [stock for stock in watchlist if stock['short_interest'] > 10]
    notification_time = datetime.strftime(datetime.now(tz), "%H:%M")

    # Find all outrageous files from today, pull all tickers from them, and if
    #   they exist, do not re-add them to outrageous stocks (don't send a second email)
    ntfctns_sent_today = []
    # Ensure path exists (otherwise throws error)
    today_path = f"{cur_wd}/bigbeta/stocks/outrageous_stocks/{cur_dt}/"
    # If the path exists, get a list of what has already been stored there.
    #   This is done to avoid sending duplicate notifications
    if os.path.exists(today_path):
        # Get list of all files. Within each file, append each ticker within each file
        #   to sent notifications list.
        files = os.listdir(today_path)
        for file in files:
            with open(f"{today_path}/{file}", "r") as f:
                fdata = json.load(f)
            for fdatum in fdata:
                ntfctns_sent_today.append(fdatum['ticker'])
    # For each outrageous stock, ensure a notification hasn't already been sent,
    #   (based on above-created list) and then send a notification about the stock
    for outrageous_stock in outrageous_stocks:
        if outrageous_stock['ticker'] not in ntfctns_sent_today:
            print(outrageous_stock)
            stock_email_blast(outrageous_stock, notification_time=notification_time)
            ###### WRITE FILES WITHIN THE OUTRAGEOUS STOCKS LOOP WITH THE STOCK'S NAME!

    # Save outrageous stocks for later analysis
    # If the path doesn't exist, create it, then write to new file
    if not os.path.exists(today_path):
        os.makedirs(today_path)
    with open(f"{today_path}/{cur_tm}.json", "w") as f:
        json.dump(outrageous_stocks, f)
    return None



def anaylze_notifications():
    """
    Finds how much the outrageous stocks moved after notification and saves that data
    to a separate file
    """

    files = os.listdir(f"{cur_wd}/bigbeta/stocks/outrageous_stocks/{cur_dt}/")
    with open(f"{cur_wd}/bigbeta/stocks/outrageous_stocks/{cur_dt}/{file}", "r") as f:
        stocks = json.load(f)
    analyzed_notifications = []
    for stock in stocks:
        eod_data = wb.get_quote(stock=stock)
        analyzed_notifications.append({stock['ticker']: float(eod_data['high'])})

    with open(f"{cur_wd}/bigbeta/stocks/outrageous_stocks/analyses/{cur_dt}.json", "w") as f:
        json.dump(analyzed_notifications, f)

    return None


def stock_email_blast(stock_dict, notification_time):
    """
    Sends an email to all users
    Args:
        None
    Returns:
        String Confirmation
    """

    with bigbeta_app.app_context():
        print('sending email')
        user_list = build_users_list()
        msg = Message('Big Mover in the Market!',
                      sender=email_sender,
                      recipients=['jonmbrenner@gmail.com'])
                      # recipients=[user_list])
        msg.body = f"""\
!!!HIGH SHORT INTEREST MOVER ALERT!!!
${stock_dict['ticker']}
Short Interest: {stock_dict['short_interest']}
Float: {stock_dict['free_float']}
Days to Cover: {stock_dict['dtc']}
Relative Volume: {stock_dict['rvol']}
News Catalysts: {stock_dict['stories']}

Last Price: {stock_dict['last_price']} collected at {cur_tm_log}
Notification kicked off at {notification_time} EST

Go get it!
- BigBeta Team
"""

        mail.send(msg)

    return None


def build_users_list():
    """
    Retrieve a list of all users to send emails to.
    Args: None
    Returns: List of users
    """

    # Cannot query in cronjob (only use case for this func) without app running.
    #   Must build separate connection to read file
    # con = sqlite3.connect(f"{cur_wd}/bigbeta/site.db")
    # cur = con.cursor()
    # users_list = [u for u in cur.execute("SELECT email FROM user;")]

    # Get app context

    with bigbeta_app.app_context():
        users = User.query.all()
    user_emails = [user.email for user in users]
    print(user_emails)

    return user_emails
