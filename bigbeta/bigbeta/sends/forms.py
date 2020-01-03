"""
Add Send form
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class SendForm(FlaskForm):
    """
    Class for a form section for a single Send
    """

    # title = StringField('Title', validators=[DataRequired()])
    title = StringField('Title')
    style = SelectField('Style', choices=[('boulder', 'boulder'), ('sport', 'sport')])
    grade = SelectField(
        'Grade',
        choices=[
            ('v1', 'v1'),
            ('v2', 'v2'),
            ('v3', 'v3'),
            ('v4', 'v4'),
            ('v5', 'v5'),
            ('v6', 'v6'),
            ('v7', 'v7'),
            ('v8', 'v8'),
            ('v9', 'v9'),
            ('v10', 'v10'),
            ('v11', 'v11'),
            ('v12', 'v12'),
            ('v13', 'v13'),
            ('v14', 'v14'),
            ('v15', 'v15'),
            ('5.10a', '5.10a'),
            ('5.10b', '5.10b'),
            ('5.10c', '5.10c'),
            ('5.10d', '5.10d'),
            ('5.11a', '5.11a'),
            ('5.11b', '5.11b'),
            ('5.11c', '5.11c'),
            ('5.11d', '5.11d'),
            ('5.12a', '5.12a'),
            ('5.12b', '5.12b'),
            ('5.12c', '5.12c'),
            ('5.12d', '5.12d'),
            ('5.13a', '5.13a'),
            ('5.13b', '5.13b'),
            ('5.13c', '5.13c'),
            ('5.13d', '5.13d'),
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Sent!")
