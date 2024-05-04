from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired, URL

class URLForm(FlaskForm):
    url = StringField('Enter URL of PDF', validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')

class UploadForm(FlaskForm):
    file = FileField('Upload PDF File', validators=[DataRequired()])
    submit = SubmitField('Upload')

class FeedbackForm(FlaskForm):
    feedback = StringField('Enter your feedback', validators=[DataRequired()])
    submit = SubmitField('Submit Feedback')
