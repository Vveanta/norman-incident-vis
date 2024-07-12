from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, RadioField, MultipleFileField
from wtforms.validators import DataRequired, URL

class URLForm(FlaskForm):
    url = StringField('Enter URL of PDF', validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')

class UploadForm(FlaskForm):
    file_type = RadioField('File Type', choices=[('csv', 'CSV'), ('pdf', 'PDF')], validators=[DataRequired()])
    file = MultipleFileField('File', validators=[DataRequired()])
    submit = SubmitField('Upload')

class FeedbackForm(FlaskForm):
    feedback = StringField('Enter your feedback', validators=[DataRequired()])
    submit = SubmitField('Submit Feedback')
