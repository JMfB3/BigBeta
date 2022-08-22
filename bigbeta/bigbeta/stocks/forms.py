"""
Watchlist forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField


class PreMktList(FlaskForm):
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
