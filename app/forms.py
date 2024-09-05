from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, RadioField, MultipleFileField,TextAreaField, EmailField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, URL, Email,ValidationError

class URLForm(FlaskForm):
    url = StringField('Enter URL of PDF', validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')
class ConditionalDataRequired(DataRequired):
    def __init__(self, exclude_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exclude_value = exclude_value

    def __call__(self, form, field):
        if form.file_type.data != self.exclude_value:
            super().__call__(form, field)

class UploadForm(FlaskForm):
    # file_type = RadioField('File Type', choices=[('csv', 'CSV'), ('pdf', 'PDF'), ('url', 'URL')], validators=[DataRequired()])
    file_type = RadioField('File Type', choices=[('csv', 'CSV'), ('pdf', 'PDF'), ('url', 'URL'), ('default_pdf', 'Default PDF')], validators=[DataRequired()])
    file = MultipleFileField('File', validators=[ConditionalDataRequired(exclude_value='default_pdf', message='File is required when not selecting a default PDF')])
    # file = MultipleFileField('File', validators=[DataRequired()])
    default_pdfs = SelectField('Default PDF Files', choices=[])
    submit = SubmitField('Upload')

class FeedbackForm(FlaskForm):
    name = StringField('Full name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    user_type = RadioField('Which Describes you the Best', choices=[('student', 'Student'), ('professor', 'Professor'), ('recruiter', 'Corporate Recruiter'), ('other', 'Other')], validators=[DataRequired()])
    rating = RadioField('Rate Your Experience', choices=[('1', '1 - Very Poor'), ('2', '2 - Poor'), ('3', '3 - Average'), ('4', '4 - Good'), ('5', '5 - Excellent')], validators=[DataRequired()])
    feedback = TextAreaField('Your Feedback', validators=[DataRequired()])
    submit = SubmitField('Submit Feedback')