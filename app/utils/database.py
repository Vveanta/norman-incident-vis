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

# Function to populate the database with incident data
def populate_db(db_path, incidents):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Insert each incident into the database
    for incident in incidents:
        c.execute("INSERT INTO incidents VALUES (?, ?, ?, ?, ?)", (incident['Incident_time'],incident['Incident Number'], incident['Location'], incident['Nature'], incident['Incident ORI']))
    conn.commit()
    conn.close()


def create_feedback_tables(db_path="resources/normanpd.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
        # Create the user_types table
    c.execute('''   
                CREATE TABLE IF NOT EXISTS user_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT UNIQUE NOT NULL
                )''')

    # Create the feedback table
    c.execute('''   
                CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                user_type_id INTEGER,
                rating TEXT,
                feedback TEXT,
                FOREIGN KEY (user_type_id) REFERENCES user_types (id)
                )''')
    # Check if the user_types table is empty
    c.execute("SELECT COUNT(*) FROM user_types")
    count = c.fetchone()[0]

    # Insert initial values into user_types only if the table is empty
    if count == 0:
        c.executemany("INSERT INTO user_types (type) VALUES (?)", [
            ('student',),
            ('professor',),
            ('recruiter',),
            ('other',)
        ])
    conn.commit()
    conn.close()