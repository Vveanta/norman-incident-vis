import csv
import logging
import sqlite3
from flask import Blueprint, render_template, request, redirect, send_from_directory, url_for, flash, jsonify
from .forms import URLForm, UploadForm, FeedbackForm
from werkzeug.utils import secure_filename
import os
import pandas as pd
from .utils import create_db, fetch_incidents, extract_incidents, populate_db, augment_data,create_feedback_tables
import urllib.error
import urllib.parse
import psycopg2
from psycopg2 import sql
import configparser



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    default_pdf_files = [(filename, filename) for filename in os.listdir('defaultpdfs')]
    upload_form = UploadForm()
    upload_form.default_pdfs.choices = default_pdf_files 
    if upload_form.validate_on_submit():
        success_count = 0
        failed_urls = []
        skipped_urls = []
        db_path = ensure_database_exists()
        file_type = request.form['file_type']
        if file_type == 'url':
            urls = request.form['urls'].splitlines()
            failed_urls,skipped_urls,success_count = process_urls(urls, db_path,success_count)
        elif file_type == 'default_pdf':
            # Handling default PDF file selected from dropdown
            selected_pdf = upload_form.default_pdfs.data
            file_path = os.path.join('defaultpdfs', selected_pdf)
            success = process_pdf(file_path, db_path)
            if not success:
                failed_urls.append(selected_pdf)
        else:
            files = request.files.getlist('file')
            for file in files:
                filename = secure_filename(file.filename)
                file_path = os.path.join('/tmp', filename)
                file.save(file_path)

                if file_type == 'csv' and filename.endswith('.csv'):
                    failed, skipped, success_count = process_csv(file_path, db_path, success_count)
                    failed_urls.extend(failed)
                    skipped_urls.extend(skipped)
                elif file_type == 'pdf' and filename.endswith('.pdf'):
                    if success_count >=3:
                        skipped_urls.append(filename)
                        continue
                    success = process_pdf(file_path, db_path)
                    if success:
                        success_count += 1
                    if not success:
                        failed_urls.append(filename)
                else:
                    flash('Unsupported file type', category='error')
                    return redirect(url_for('main.upload'))

        csv_file_path = augment_data(db_path)
        return redirect(url_for('main.results', csv_file_path=csv_file_path, failed_urls=urllib.parse.quote_plus(','.join(failed_urls)), skipped_urls=urllib.parse.quote_plus(','.join(skipped_urls))))
    return render_template('upload.html', upload_form=upload_form)

def process_urls(urls, db_path, success_count):
    failed_urls = []
    skipped_urls=[]
    for url in urls:
        if success_count >= 3:
            skipped_urls.append(url)
            continue
        pdf_filename = fetch_pdf(url)
        if pdf_filename is None:
            logger.warning(f"Skipping URL: {url} due to fetch failure.")
            failed_urls.append(url)
            continue

        try:
            incidents = extract_incidents(pdf_filename)
            populate_db(db_path, incidents)
            success_count += 1
        except ValueError as e:
            logger.warning(f"Error extracting incidents from URL: {url} - {e}")
            failed_urls.append(url)

    return failed_urls, skipped_urls, success_count

def process_csv(file_path, db_path,success_count):
    urls = pd.read_csv(file_path, header=None)
    return process_urls(urls[0], db_path,success_count)

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
    skipped_urls = urllib.parse.unquote_plus(request.args.get('skipped_urls', '')).split(',')
    data = get_augmented_data(csv_file_path)
    conn = sqlite3.connect('resources/normanpd.db')
    cursor = conn.cursor()
    cursor.execute('SELECT location, latitude, longitude, COUNT(*) as count FROM incidents JOIN geocodes ON incidents.incident_location = geocodes.location GROUP BY location')
    locations = cursor.fetchall()
    conn.close()
    # Convert to a format that can be easily used in the template
    locations_data = [{'location': loc[0], 'latitude': loc[1], 'longitude': loc[2], 'count': loc[3]} for loc in locations]
    return render_template('results.html', data=data, csv_url=csv_file_path, failed_urls=failed_urls,skipped_urls=skipped_urls,locations=locations_data)
    # return redirect("http://localhost:8501", code=302)

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
        create_feedback_tables() 
        logger.info("Handling POST request and form validation")
        user_type = feedback_form.user_type.data # Assuming single selection for simplicity
        logger.info(f"Received user type from form: {user_type}")
        # Connect to SQLite database
        conn = sqlite3.connect('resources/normanpd.db')
        cur = conn.cursor()
        # Get user_type_id from user_types table
        cur.execute("SELECT id FROM user_types WHERE type = ?", (user_type,))
        user_type_id = cur.fetchone()

        if user_type_id:
            # Prepare feedback data to be inserted
            # Prepare feedback data to be inserted
            feedback_data = (
                feedback_form.name.data,
                feedback_form.email.data,
                user_type_id[0],
                feedback_form.rating.data,
                feedback_form.feedback.data
            )
            logger.info(f"Feedback data: {feedback_data}")

            # Insert feedback data into feedback table
            cur.execute('''
                INSERT INTO feedback (name, email, user_type_id, rating, feedback)
                VALUES (?, ?, ?, ?, ?)
            ''', feedback_data)
            conn.commit()
            cur.close()
            conn.close()
            return jsonify(status='success')
        else:
            return jsonify(status='failure', message='Invalid user type')

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
