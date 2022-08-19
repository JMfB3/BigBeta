"""
Stocks Page?
"""

from flask_wtf import FlaskForm


class SendForm(FlaskForm):
    """
    Class for a form section for a single Send
    """

    # title = StringField('Title', validators=[DataRequired()])
    title = StringField('Title')
    style = SelectField('Style', choices=[('boulder', 'boulder'), ('sport', 'sport')])
        validators=[DataRequired()]
    )
