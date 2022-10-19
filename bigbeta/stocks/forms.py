"""
Watchlist forms
"""

from flask_wtf import FlaskForm
from wtforms import Field, StringField, DecimalField, IntegerField, SubmitField


class Watchlist(FlaskForm):
    """
    Pre Market Gainers
    """

    # id = IntegerField
    ticker = StringField('Ticker')
    name = StringField('Name')
    rvol = DecimalField('RVOL')
    freefloat = IntegerField('Free Float')
    short_interest = DecimalField('Short Interest')
    si_raw = IntegerField('Short Interest Raw')
    dtc = DecimalField('Days to Cover')
    stories = IntegerField('Recent News Stories')


class SearchForm(FlaskForm):
    """
    Class for form to search for tickers
    """

    tckr_input = StringField('Search any ticker to add to your watchlist')
    submit = SubmitField("Search")


# class RemoveStockForm(FlaskForm):
#     """
#     Just trying to create a button to remove a table item
#     """
#     tckr_input = StringField()
#     submit = SubmitField("Remove")
