import os
import json
from datetime import datetime, date, timedelta
from pytz import timezone
import pandas as pd
import requests
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup as bs
from webull import webull
from flask import current_app


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
# Use for prod
if not wb_user:
    with open('/etc/config.json') as config_file:
        config = json.load(config_file)
    wb_user = config.get('WB_USER')
if not wb_pass:
    with open('/etc/config.json') as config_file:
        config = json.load(config_file)
    wb_pass = config.get('WB_PASS')
wb.login(username=wb_user, password=wb_pass)
########## End login block


def build_watchlist(wl_cnt=15, dir="gainer"):
    """
    Builds a watchlist with my fave data points. Customize by premarket, 5 min, etc
    Rank Types: preMarket / afterMarket / 5min / 1d / 5d / 1m / 3m / 52w
    """

    # Determine which watchlist to build (premarket, 1d, afterhours)
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

    # Ping WeBull
    print('running...')
    l_watchlist = []
    premkt_gnrs = wb.active_gainer_loser(direction=dir, rank_type=rank_type, count=wl_cnt)
    # Odd wb output requires some data maniuplation
    ### Must dig into list within list
    l_tickers = [r["ticker"]["symbol"] for r in premkt_gnrs["data"]]
    for ticker in l_tickers:
        ticker_dct = fundamentals(ticker)
        #### Add to full DF to be reported at end of processing
        l_watchlist.append(ticker_dct)

    # Write data out to file for storage
    with open(f"{cur_wd}/history/dt_{cur_dt}__tm__{cur_tm}.json", "w") as f:
        json.dump(l_watchlist, f)
    # Write it out again to an overwritten file for easy retrieval
    with open(f"{cur_wd}/current_run/current_data.json", "w") as f:
        json.dump(l_watchlist, f)
    with open(f"{cur_wd}/current_run/last_run.txt", "w") as f:
        f.write(f"{rank_type} at {cur_tm_log} EST")

    return l_watchlist


def get_stock(ticker):
    l = []
    f = fundamentals(ticker)
    l.append(f)
    fdf = pd.DataFrame(l)
    print(datetime.now().strftime("%H:%M:%S"))
    print(fdf)
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
        # Manipulate as needed
        ### Free float
        ffs = round((int(fff) / 1000000), 2)
        ### RVOL
        try:
            rvol = round(int(vol) / int(avg_vol), 2)
        except ZeroDivisionError:
            rvol = 0

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
            print(mw_data)
            si_raw = mw_data['si_raw']
            dtc = mw_data['dtc']
            # si_raw = mw_data['']
            si_pct = mw_data['si_pct']

            # si_ = 0
            # dtc = 0
            # si_raw = 0
            # si_pct = 0

        # Get number of relevant news stories
        #   Maybe add top story to the final DF
        news_stories = get_news(ticker, cnm)

        ticker_dct = {
            'ticker': ticker,
            'name': cnm,
            'rvol': rvol,
            'free_float': f"{str(ffs)}M",
            'short_interest': f"{str(si_pct)}%",
            'si_raw': "{:,}".format(int(si_raw)),
            'dtc': dtc,
            'stories': news_stories,
            }

        return ticker_dct


# def shorts_screener():
#     """
#     Build a watchlist based on short interest
#     """
#
#     yahoo_pg = requests.get("https://finance.yahoo.com/screener/predefined/most_shorted_stocks/")


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


# def get_trades():
#     activities = wb.get_activities()
#     l = activities['items']
#     df = pd.DataFrame(l)
#
#     return df

# def death_drop(a, b):
#     return (a + b) / 2
