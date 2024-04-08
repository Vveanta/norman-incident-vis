import csv

# List of URLs
urls = [
    "https://www.normanok.gov/sites/default/files/documents/2024-04/2024-03-31_daily_incident_summary.pdf",
    "https://www.normanok.gov/sites/default/files/documents/2024-04/2024-03-25_daily_incident_summary.pdf",
    # "https://example.com/page3",
    # "https://example.com/page4",
    # "https://example.com/page5"
]

# File path for the CSV
csv_file = "files.csv"

# Writing URLs to CSV
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    # writer.writerow(["URLs"])  # Write header
    for url in urls:
        writer.writerow([url])