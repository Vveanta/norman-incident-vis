import sqlite3
# Function to create the database and table for storing incidents
def create_db(db_path="resources/normanpd.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Reset the table if it exists
    c.execute('DROP TABLE IF EXISTS incidents;')
    # Create the incidents table
    c.execute('''   
                 CREATE TABLE IF NOT EXISTS incidents (
                 incident_time TEXT,
                 incident_number TEXT,
                 incident_location TEXT,
                 nature TEXT,
                 incident_ori TEXT
                 )''')
    conn.commit()
    conn.close()

import sqlite3
# Function to populate the database with incident data
def populate_db(db_path, incidents):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Insert each incident into the database
    for incident in incidents:
        c.execute("INSERT INTO incidents VALUES (?, ?, ?, ?, ?)", (incident['Incident_time'],incident['Incident Number'], incident['Location'], incident['Nature'], incident['Incident ORI']))
    conn.commit()
    conn.close()