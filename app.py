import streamlit as st
import requests
import xmltodict
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="VAST Tag Inspector",
    layout="wide"
)

# --- HELPER FUNCTIONS ---
def fetch_vast(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return str(e)

def parse_vast(xml_content):
    try:
        # Convert XML to Python Dictionary
        data = xmltodict.parse(xml_content)
        
        # Navigate through standard VAST structure to find MediaFiles
        # Note: VAST structure can vary, this is a simplified traversing for InLine ads
        vast_root = data.get('VAST', {})
        ad = vast_root.get('Ad', {})
        
        # Handle cases with multiple ads, take the first one
        if isinstance(ad, list):
            ad = ad[0]
            
        inline = ad.get('InLine', {})
        creatives = inline.get('Creatives', {}).get('Creative', {})
        
        # Handle list of creatives
        if isinstance(creatives, list):
            linear = None
            for c in creatives:
                if 'Linear' in c:
                    linear = c['Linear']
                    break
        else:
            linear = creatives.get('Linear', {})

        if not linear:
            return None, "No Linear Creative found in VAST."

        # Extract Media Files
        media_files = linear.get('MediaFiles', {}).get('MediaFile', [])
        if not isinstance(media_files, list):
            media_files = [media_files]

        return {
            "version": vast_root.get('@version', 'Unknown'),
            "title": inline.get('AdTitle', 'Unknown'),
            "description": inline.get('Description', ''),
            "duration": linear.get('Duration', '00:00:00'),
            "media_files": media_files,
            "impressions": inline.get('Impression', [])
        }, None

    except Exception as e:
        return None, f"Parsing Error: {str(e)}"

# --- UI LAYOUT ---

st.title("VAST Tag Inspector & Player")
st.markdown("Analyze Video Ad Serving Template (VAST) XML tags and debug video creatives.")

# Input
vast_url = st.text_input("Enter VAST Tag URL", placeholder="https://example.com/vast.xml")

# Quick Test Button (Pre-fill for demo purposes)
if st.button("Use Sample Google VAST Tag"):
    vast_url = "https://pubads.g.doubleclick.net/gampad/ads?sz=640x480&iu=/124319096/external/single_ad_samples&ciu_szs=300x250&impl=s&gdfp_req=1&env=vp&output=vast&unviewed_position_start=1&cust_params=deployment%3Ddevsite%26sample_ct%3Dlinear&correlator="
    st.info("Sample URL loaded. Press 'Analyze' below.")
    st.code(vast_url)

if st.button("Analyze VAST"):
    if not vast_url:
        st.warning("Please enter a URL.")
    else:
        with st.spinner("Fetching and Parsing XML..."):
            raw_xml = fetch_vast(vast_url)
            
            if raw_xml.startswith("http") or "Error" in raw_xml[:20]:
                st.error(f"Failed to load VAST: {raw_xml}")
            else:
                data, error = parse_vast(raw_xml)
                
                if error:
                    st.error(error)
                    with st.expander("View Raw XML"):
                        st.code(raw_xml, language='xml')
                else:
                    # --- RESULTS ---
                    st.divider()
                    
                    # 1. Header Info
                    c1, c2, c3 = st.columns(3)
                    c1.metric("VAST Version", data['version'])
                    c2.metric("Duration", data['duration'])
                    c3.metric("Ad Title", data['title'])
                    
                    # 2. Video Player
                    st.subheader("Creative Preview")
                    
                    # Find the best MP4 file to play
                    mp4_url = None
                    for mf in data['media_files']:
                        # Check if #text exists (xmltodict structure) and is mp4
                        url = mf.get('#text', '')
                        mime = mf.get('@type', '')
                        if 'mp4' in mime or '.mp4' in url:
                            mp4_url = url
                            break
                    
                    if mp4_url:
                        st.video(mp4_url)
                        st.success(f"Playing source: {mp4_url}")
                    else:
                        st.warning("No compatible MP4 media file found for web playback.")

                    # 3. Media Files Table
                    st.subheader("Media Files Technical Data")
                    
                    # Clean up data for table
                    table_data = []
                    for mf in data['media_files']:
                        table_data.append({
                            "Type": mf.get('@type'),
                            "Bitrate": mf.get('@bitrate'),
                            "Width": mf.get('@width'),
                            "Height": mf.get('@height'),
                            "URL": mf.get('#text')
                        })
                    
                    st.table(table_data)

                    # 4. Debug Data
                    with st.expander("View Raw XML & JSON"):
                        tab1, tab2 = st.tabs(["XML Source", "Parsed JSON"])
                        with tab1:
                            st.code(raw_xml, language='xml')
                        with tab2:
                            st.json(data)
