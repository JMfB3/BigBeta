"""
This hosts all forms related to climbs for the BigBeta site
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, FieldList, StringField, SubmitField
from wtforms.validators import DataRequired


class AddClimbForm(FlaskForm):
    """
    Class for the add climb form.
    This form will serve to add climbs to the database.
    You should be able to add all the climbs you did for a single session,
        and view your climbs added as you continue to add them.
        There should be no separation here between sport and bouldering.
    """

    title = StringField('Title', validators=[DataRequired()])
    add_climb = FieldList(StringField(
        'Add Climbs',
        render_kw=[
            'v1',
            'v2',
        ]
        validators=[DataRequired()]))
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField("Post")
