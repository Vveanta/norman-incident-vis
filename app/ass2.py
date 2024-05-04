from app.utils import fetch_incidents, extract_incidents, populate_db, augment_data, create_db
import argparse
import pandas as pd
import os
def main(urls_file):


    urls = pd.read_csv(urls_file, header=None, index_col=False)
    if not os.path.exists('resources'):
        os.makedirs('resources')
    db_path = "resources/normanpd.db"
    # Create new database (if not exists)
    create_db(db_path)
    for url in urls[0]:
        pdf_filename = "/tmp/incident.pdf"  # Example path, (path to store temporary pdf files)
        # Download data
        
        fetch_incidents(url, pdf_filename)

        # Extract data
        incidents = extract_incidents(pdf_filename)
        # Insert data
        populate_db(db_path, incidents)
    # print('check1')
    # augmented_incidents = augment_data(db_path)
    augment_data(db_path)
    # # with open('output_txt.txt', 'w') as output_file:
    # #     for incident in augmented_incidents:
    # #         output_file.write(str(incident) + '\n')
    # print("Day of the Week\tTime of Day\tWeather\tLocation Rank\tSide of Town\tIncident Rank\tNature\tEMSSTAT")

    # # Iterate through augmented incidents and print each one in the specified format
    # for incident in augmented_incidents:
    #     print(f"{incident['Day Of The Week']}\t"
    #         f"{incident['Time Of Day']}\t"
    #         f"{incident['Weather']}\t"
    #         f"{incident['Location Rank']}\t"
    #         f"{incident['Side of Town']}\t"
    #         f"{incident['Nature Rank']}\t"
    #         f"{incident['Nature']}\t"
    #         f"{1 if incident['EMSSTAT'] else 0}")
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", type=str, required=True, help="CSV file containing PDF URLs.")
     
    args = parser.parse_args()
    if args.urls:
        main(args.urls)
