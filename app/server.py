from flask import Blueprint, render_template, request, redirect, send_from_directory, url_for, flash
from .forms import URLForm, UploadForm, FeedbackForm
from werkzeug.utils import secure_filename
import os
import pandas as pd
from .utils import create_db, fetch_incidents, extract_incidents, populate_db, augment_data

# from .utils import process_pdf  # You'll write this function to handle PDF processing

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        db_path = ensure_database_exists()
        files = request.files.getlist('file')  # Get list of files

        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join('/tmp', filename)
            file.save(file_path)

            if filename.endswith('.csv'):
                process_csv(file_path, db_path)
            elif filename.endswith('.pdf'):
                process_pdf(file_path, db_path)
            else:
                flash('Unsupported file type', category='error')
                return redirect(url_for('main.upload'))

        csv_file_path = augment_data(db_path)
        return redirect(url_for('main.results', csv_file_path=csv_file_path))
    return render_template('upload.html', form=form)

def process_csv(file_path, db_path):
    urls = pd.read_csv(file_path, header=None)
    for url in urls[0]:
        pdf_filename = fetch_pdf(url)
        incidents = extract_incidents(pdf_filename)
        populate_db(db_path, incidents)

def fetch_pdf(url):
    local_filename = os.path.join('/tmp', url.split('/')[-1].split('.')[0])
    fetch_incidents(url, local_filename)
    return local_filename

def process_pdf(pdf_filename, db_path):
    incidents = extract_incidents(pdf_filename)
    populate_db(db_path, incidents)

def ensure_database_exists():
    db_path = "resources/normanpd.db"
    if not os.path.exists('resources'):
        os.makedirs('resources')
    create_db(db_path)
    return db_path

@main.route('/results')
def results():
    csv_file_path = request.args.get('csv_file_path')
    return render_template('results.html', csv_file_path=csv_file_path)

@main.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory('resources', filename, as_attachment=True)

@main.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        # Process feedback here
        # Store or log the feedback
        return redirect(url_for('main.thankyou'))  
    return render_template('feedback.html', form=form)
@main.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')