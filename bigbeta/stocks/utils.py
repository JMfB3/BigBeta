import os
from datetime import datetime, date, timedelta
from webull import webull
import pandas as pd
import requests
from fuzzywuzzy import fuzz
from flask import current_app


wb = webull()
wb_user = os.environ.get('WB_USER')
wb_pass = os.environ.get('WB_PASS')
wb.login(username=wb_user, password=wb_pass)


def build_watchlist(rank_type='preMarket', wl_cnt=15, dir="gainer"):
    """
    Builds a watchlist with my fave data points. Customize by premarket, 5 min, etc
    Rank Types: preMarket / afterMarket / 5min / 1d / 5d / 1m / 3m / 52w
    """
    ### Pre Market gainers
    # Ping WeBull
    print('running...')
    l_watchlist = []
    premkt_gnrs = wb.active_gainer_loser(direction=dir, rank_type=rank_type, count=wl_cnt)
    # Odd wb output requires some data maniuplation
    ### Must dig into list within list
    l_tickers = [r["ticker"]["symbol"] for r in premkt_gnrs["data"]]
    for ticker in l_tickers:
        ticker_dct = fundamentals(ticker)
        # Print tickers as they are loaded, rather than waiting for them all
        # tmp_l = []
        # tmp_l.append(ticker_dct)
        # tmp_df = pd.DataFrame(tmp_l)
        # print(tmp_df)
        #### Add to full DF to be reported at end of processing
        l_watchlist.append(ticker_dct)

    # watchlist_df = pd.DataFrame(l_watchlist)

    # print(datetime.now().strftime("%H:%M:%S"))
    print(l_watchlist)

    return l_watchlist


# wb.get_financials(stock='SOUN')

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
            si_ = 0
            dtc = 0
            si_raw = 0
            si_pct = 0

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


def shorts_screener():
    """
    Build a watchlist based on short interest
    """

    yahoo_pg = requests.get("https://finance.yahoo.com/screener/predefined/most_shorted_stocks/")


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


def get_trades():
    activities = wb.get_activities()
    l = activities['items']
    df = pd.DataFrame(l)

    return df

def death_drop(a, b):
    return (a + b) / 2
