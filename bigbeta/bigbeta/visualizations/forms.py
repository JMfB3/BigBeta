"""
visualizations forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class VisualizationForm(FlaskForm):
    """
    Class for a form section for a visualization
    """

    content = TextAreaField('Visualization')
