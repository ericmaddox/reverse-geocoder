import pandas as pd
import argparse
import os
import csv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
from datetime import datetime
from io import StringIO

# Initialize the geocoder with a descriptive user agent required by Nominatim
geolocator = Nominatim(user_agent="reverse_geocoder")

# Dictionary to map full state names to abbreviations (for fallback)
STATE_ABBREVS = {
    'Georgia': 'GA', 'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# Function to handle geocoding with retry on timeout and delay. Nominatim requires a 1 second delay between requests.
def reverse_geocode(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), timeout=10)
        time.sleep(1)  # Delay to respect Nominatim's usage policy
        if location and location.raw.get('address'):
            addr = location.raw['address']
            # Extract desired components
            house_number = addr.get('house_number', '')
            street = addr.get('road', '')
            city = addr.get('city', addr.get('town', addr.get('village', '')))
            state = addr.get('state', '')
            postcode = addr.get('postcode', '')
            # Get state abbreviation
            state_abbrev = STATE_ABBREVS.get(state, state[:2].upper() if state else '')
            # Combine house number and street if both exist
            street_address = f"{house_number} {street}".strip() if house_number and street else street or house_number
            # Format as "numerical address, street, city, state, zip"
            return f"{street_address}, {city}, {state_abbrev}, {postcode}".strip(', ')
        return "Address not found"
    except GeocoderTimedOut:
        time.sleep(1)
        return reverse_geocode(lat, lon)

def clean_rtf_content(file_path):
    """Attempt to extract CSV content from RTF file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Check for RTF markers
    if content.startswith('{\\rtf'):
        # Extract lines that look like CSV (latitude,longitude pairs)
        lines = content.splitlines()
        csv_lines = [line for line in lines if ',' in line and any(c.isdigit() for c in line)]
        # Ensure header is included
        if not csv_lines or 'latitude,longitude' not in content:
            csv_lines.insert(0, 'latitude,longitude')
        return '\n'.join(csv_lines)
    return content

def detect_delimiter(content):
    """Detect the delimiter (comma or tab) using csv.Sniffer."""
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(content[:1024])  # Sniff first 1024 characters
        return dialect.delimiter
    except csv.Error:
        # Fallback to trying comma or tab
        return ',' if ',' in content.splitlines()[0] else '\t'

def main():
    parser = argparse.ArgumentParser(description="Reverse geocode lat/long CSV to addresses.")
    parser.add_argument("input_csv", help="Path to input CSV or TXT file with 'latitude' and 'longitude' columns.")
    args = parser.parse_args()

    input_path = args.input_csv

    # Validate file extension
    if not input_path.lower().endswith(('.csv', '.txt')):
        print("Error: Input file must have a .csv or .txt extension.")
        return

    # Clean RTF content if necessary
    try:
        content = clean_rtf_content(input_path)
        # Detect delimiter
        delimiter = detect_delimiter(content)
        # Load the CSV from cleaned content
        df = pd.read_csv(StringIO(content), delimiter=delimiter, quoting=csv.QUOTE_ALL, on_bad_lines='warn')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        print("Check CSV for correct delimiter (comma or tab), 'latitude', 'longitude' columns, and plain text format (not RTF).")
        return

    # Validate required columns (case-insensitive)
    required_columns = {'latitude', 'longitude'}
    actual_columns = {col.lower() for col in df.columns}
    if not required_columns.issubset(actual_columns):
        print("CSV columns:", df.columns.tolist())
        raise ValueError("CSV must include 'latitude' and 'longitude' columns (case-insensitive).")

    # Rename columns to lowercase for consistency
    df.columns = [col.lower() for col in df.columns]

    # Reverse geocode each row
    df['address'] = df.apply(lambda row: reverse_geocode(row['latitude'], row['longitude']), axis=1)

    # Generate unique output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = f"geocodeoutput_{timestamp}.csv"
    output_path = os.path.join(script_dir, output_filename)

    # Save to output CSV
    df.to_csv(output_path, index=False)

    # Summary
    print(f"Geocoding complete. {len(df)} row(s) processed.")
    print(f"Output saved as: {output_path}")

if __name__ == "__main__":
    main()