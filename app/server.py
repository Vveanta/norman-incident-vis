import csv
import logging
from flask import Blueprint, render_template, request, redirect, send_from_directory, url_for, flash, jsonify
from .forms import URLForm, UploadForm, FeedbackForm
from werkzeug.utils import secure_filename
import os
import pandas as pd
from .utils import create_db, fetch_incidents, extract_incidents, populate_db, augment_data
import urllib.error
import urllib.parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    upload_form = UploadForm()
    if upload_form.validate_on_submit():
        db_path = ensure_database_exists()
        file_type = request.form['file_type']
        failed_urls = []

        if file_type == 'url':
            urls = request.form['urls'].splitlines()
            failed_urls = process_urls(urls, db_path)
        else:
            files = request.files.getlist('file')
            for file in files:
                filename = secure_filename(file.filename)
                file_path = os.path.join('/tmp', filename)
                file.save(file_path)

                if file_type == 'csv' and filename.endswith('.csv'):
                    failed_urls.extend(process_csv(file_path, db_path))
                elif file_type == 'pdf' and filename.endswith('.pdf'):
                    success = process_pdf(file_path, db_path)
                    if not success:
                        failed_urls.append(filename)
                else:
                    flash('Unsupported file type', category='error')
                    return redirect(url_for('main.upload'))

        csv_file_path = augment_data(db_path)
        return redirect(url_for('main.results', csv_file_path=csv_file_path, failed_urls=urllib.parse.quote_plus(','.join(failed_urls))))
    return render_template('upload.html', upload_form=upload_form)

def process_urls(urls, db_path):
    failed_urls = []
    for url in urls:
        pdf_filename = fetch_pdf(url)
        if pdf_filename is None:
            logger.warning(f"Skipping URL: {url} due to fetch failure.")
            failed_urls.append(url)
            continue

        try:
            incidents = extract_incidents(pdf_filename)
            populate_db(db_path, incidents)
        except ValueError as e:
            logger.warning(f"Error extracting incidents from URL: {url} - {e}")
            failed_urls.append(url)

    return failed_urls

def process_csv(file_path, db_path):
    urls = pd.read_csv(file_path, header=None)
    return process_urls(urls[0], db_path)

def fetch_pdf(url):
    local_filename = os.path.join('/tmp', url.split('/')[-1].split('.')[0])
    try:
        fetch_incidents(url, local_filename)
    except urllib.error.HTTPError as e:
        logger.error(f"HTTPError: {e.code} - {e.reason} for URL: {url}")
        return None
    except urllib.error.URLError as e:
        logger.error(f"URLError: {e.reason} for URL: {url}")
        return None
    return local_filename

def process_pdf(pdf_filename, db_path):
    try:
        incidents = extract_incidents(pdf_filename)
        populate_db(db_path, incidents)
        return True  # Return True if processing is successful
    except ValueError as e:
        logger.error(f"Error processing PDF {pdf_filename}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_filename}: {e}")
        return False

def ensure_database_exists():
    db_path = "resources/normanpd.db"
    if not os.path.exists('resources'):
        os.makedirs('resources')
    create_db(db_path)
    return db_path

@main.route('/results')
def results():
    csv_file_path = request.args.get('csv_file_path')
    failed_urls = urllib.parse.unquote_plus(request.args.get('failed_urls', '')).split(',')
    data = get_augmented_data(csv_file_path)
    return render_template('results.html', data=data, csv_url=csv_file_path, failed_urls=failed_urls)

@main.route('/download/<path:filename>')
def download_file(filename):
    directory = os.path.join(main.root_path, 'resources')
    logger.info(f"Attempting to send file from directory: {directory}, filename: {filename}")
    return send_from_directory(directory, filename, as_attachment=True)

@main.route('/feedback', methods=['GET', 'POST'])
def feedback():
    feedback_form = FeedbackForm()
    logger.info("Entered feedback route")

    if request.method == 'POST' and feedback_form.validate_on_submit():
        logger.info("Handling POST request and form validation")
        feedback_data = {
            "name": feedback_form.name.data,
            "email": feedback_form.email.data,
            "user_type": feedback_form.user_type.data,
            "rating": feedback_form.rating.data,
            "feedback": feedback_form.feedback.data
        }
        logger.info(f"Feedback data: {feedback_data}")
        return jsonify(status='success')
    return render_template('feedback.html', feedback_form=feedback_form)

@main.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

def get_augmented_data(csv_file_path):
    data = []
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data
