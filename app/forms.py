from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, RadioField, MultipleFileField,TextAreaField, EmailField, SelectMultipleField
from wtforms.validators import DataRequired, URL, Email

class URLForm(FlaskForm):
    url = StringField('Enter URL of PDF', validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')

class UploadForm(FlaskForm):
    file_type = RadioField('File Type', choices=[('csv', 'CSV'), ('pdf', 'PDF'), ('url', 'URL')], validators=[DataRequired()])
    file = MultipleFileField('File', validators=[DataRequired()])
    submit = SubmitField('Upload')

class FeedbackForm(FlaskForm):
    name = StringField('Full name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    user_type = RadioField('Which Describes you the Best', choices=[('student', 'Student'), ('professor', 'Professor'), ('recruiter', 'Corporate Recruiter'), ('other', 'Other')], validators=[DataRequired()])
    rating = RadioField('Rate Your Experience', choices=[('1', '1 - Very Poor'), ('2', '2 - Poor'), ('3', '3 - Average'), ('4', '4 - Good'), ('5', '5 - Excellent')], validators=[DataRequired()])
    feedback = TextAreaField('Your Feedback', validators=[DataRequired()])
    submit = SubmitField('Submit Feedback')