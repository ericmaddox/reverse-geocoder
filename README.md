# Reverse Geocoder

A Python utility that reads a CSV or TXT file containing latitude and longitude coordinates and uses the Nominatim (OpenStreetMap) service to convert them into simplified physical addresses (numerical address, street, city, state abbreviation, ZIP code).

## Features

- Reverse geocoding using the free Nominatim API.
- Supports input from `.csv` or `.txt` files with `latitude` and `longitude` columns.
- Outputs results to a CSV file with a timestamped filename (e.g., `geocodeoutput_YYYYMMDD_HHMMSS.csv`).
- Extracts simplified addresses: numerical address, street, city, state abbreviation (e.g., "GA"), and ZIP code.
- Handles RTF-formatted input files by extracting CSV data.
- Command-line interface with `argparse`.
- Automatically saves output in the same directory as the script.

## Requirements

- Python 3.6+
- `geopy`
- `pandas`

## Installation

Clone the repository and install the required packages:

```bash
git clone https://github.com/ericmaddox/reverse-geocoder.git
cd reverse-geocoder
pip install -r requirements.txt
```

## Usage

Prepare a CSV or TXT file (e.g., `locations.csv` or `locations.txt`) with the following structure:

```
latitude,longitude
33.7490,-84.3880
32.0835,-81.0998
```

Run the script:

```bash
python3 reverse_geocoder.py locations.csv
```

or

```bash
python3 reverse_geocoder.py locations.txt
```

- The output file will be saved as `geocodeoutput_YYYYMMDD_HHMMSS.csv` in the same directory as the script.

## Example

**Input** (`georgia_sample.csv`):

```
latitude,longitude
33.7490,-84.3880
32.0835,-81.0998
```

**Output** (`geocodeoutput_20250506_190109.csv`):

```
latitude,longitude,address
33.7490,-84.3880,"206 Washington Street Southwest, Atlanta, GA, 30334"
32.0835,-81.0998,"3121 Barnard Street, Savannah, GA, 31401"
```

## Notes

- The script uses Nominatim and adheres to OpenStreetMap’s usage policy, including a 1-second delay between requests.
- For large datasets, ensure compliance with Nominatim’s rate limits to avoid being blocked.
- The script handles RTF-formatted input files by extracting CSV data, but plain CSV or TXT files are preferred for reliability.
- State names (e.g., "Georgia") are mapped to abbreviations (e.g., "GA") for consistent output.
- If the address components (e.g., house number, street) are unavailable, the script returns "Address not found" or partial data.

## License

This project is licensed under the MIT License.
