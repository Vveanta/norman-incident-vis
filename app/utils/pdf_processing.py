import urllib.request
# Function to fetch incident PDFs from a specified URL
def fetch_incidents(url, filename):
    # Set up a user agent to prevent request being blocked
    headers = {'User-Agent': "Mozilla/5.0"}
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    data = response.read()
    # Write the data to a file
    with open(filename, 'wb') as file:
        file.write(data)

import PyPDF2 # type: ignore
import re
import fitz  # type: ignore # PyMuPDF
# Function to extract incidents from the downloaded PDF
def extract_incidents(pdf_file_path):
    doc = fitz.open(pdf_file_path)
    all_text = ""
    # Extract text from each page
    for page in doc:
        all_text += page.get_text()
    doc.close()
    # Prepare lines for processing
    lines = all_text.split('\n')
    lines = [line.strip() for line in lines]
    # Filter out header and footer lines
    lines = [line for line in lines if 'NORMAN POLICE DEPARTMENT' not in line and "Daily Incident Summary (Public)" not in line and line != "RAMP"]
    incidents = []
    # Regex pattern to identify the date and time format
    date_pattern = re.compile(r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}')

    i=5
    # Iterate through lines to extract incident details
    while i < len(lines):
        # Use regex to check if the line starts with a date and time
        if i + 3 < len(lines) and date_pattern.match(lines[i]):
            incident_time = lines[i]
            incident_number = lines[i + 1]
            # Default values for missing data
            location = "/"  # Default value
            nature = "/"    # Default value
            incident_ori = "/"  # Default value
            # Logic to handle missing data fields
            if i + 2 < len(lines) and not date_pattern.match(lines[i + 2]):
                if i + 3 < len(lines) and not date_pattern.match(lines[i + 3]):
                    if i + 4 < len(lines) and not date_pattern.match(lines[i + 4]):
                        location = lines[i + 2]
                        nature = lines[i + 3]
                        incident_ori = lines[i + 4]
                        i+=5
                    else:
                        location = lines[i + 2]
                        incident_ori = lines[i + 3]
                        i+=4
                else:
                    incident_ori = lines[i+2]
                    i+=3

            else:
                # Handle cases where either location or nature is missing
                incident_ori = lines[i + (2 if location == "/" else 3)].strip()
                i += (4 if location == "/" or nature == "/" else 5)
            # Add the incident to the list
            incident = {
                'Incident_time': incident_time,
                'Incident Number': incident_number,
                'Location': location,
                'Nature': nature,
                'Incident ORI': incident_ori,
            }
            incidents.append(incident)
        else:
            i += 1  # Increment to avoid infinite loop
    return incidents