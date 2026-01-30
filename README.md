# VAST Tag Inspector

A diagnostic tool for AdOps professionals to validate Video Ad Serving Template (VAST) XML responses. This application fetches VAST tags, parses the XML structure, validates media files, and attempts to render the video creative directly in the browser.

## Features

* **XML Parsing:** Converts complex VAST XML into structured JSON data.
* **Creative Preview:** Automatically extracts `MP4` nodes and plays the video ad for visual verification.
* **Technical Analysis:** Displays detailed table of all `MediaFiles` (Bitrate, Resolution, MIME Types).
* **Deep Debugging:** Provides raw XML and parsed JSON views for troubleshooting.

## Tech Stack

* **Python 3**
* **Streamlit**
* **Xmltodict** (for efficient XML-to-Dictionary conversion)
* **Requests**

## Usage

1. Install requirements: `pip install -r requirements.txt`
2. Run the app: `streamlit run app.py`
3. Enter a VAST Tag URL (or use the built-in Google Sample).
