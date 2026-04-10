import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time
import pandas as pd
import os
import urllib.parse  # Message encoding ke liye zaroori hai

# Page Setup
st.set_page_config(page_title="Het's Ultimate Cloud Bot", layout="wide")
st.title("📲 Het's WhatsApp Bulk Sender (Cloud Version)")
st.write("Gujarati Message + Link support ke sath!")

# --- Selenium Setup for Cloud ---
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    options.binary_location = "/usr/bin/chromium"
    
    try:
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        st.error(f"Driver Error: {e}")
        return None

if 'driver' not in st.session_state:
    st.session_state.driver = None

col1, col2 = st.columns(2)

# --- STEP 1: LOGIN ---
with col1:
    st.header("Step 1: Login")
    if st.button("Generate QR Code"):
        st.session_state.driver = setup_driver()
        st.session_state.driver.get("https://web.whatsapp.com")
        with st.spinner("Loading QR Code... (30-40 sec wait)"):
            time.sleep(40) # Cloud par WhatsApp load hone mein time leta hai
            st.session_state.driver.save_screenshot("qr.png")
            st.image("qr.png", caption="Mobile se scan karein")
            st.info("Scan hone ke baad 10 second rukiye, phir Step 2 dabayein.")

# --- STEP 2: SENDING ---
with col2:
    st.header("Step 2: Sending")
    if st.button("Start Bulk Sending"):
        if not st.session_state.driver:
            st.error("Pehle QR scan karke login karein!")
        elif not os.path.exists("leads.csv"):
            st.error("leads.csv file nahi mili! GitHub par upload karein.")
        else:
            df = pd.read_csv("leads.csv")
            st.info(f"Total {len(df)} contacts process ho rahe hain...")
            progress_bar = st.progress(0)
            
            for index, row in df.iterrows():
                phone = str(row['Phone']).replace("+", "").strip()
                raw_message = str(row['Message'])
                
                # Encoding Gujarati + Link for safe URL
                encoded_message = urllib.parse.quote(raw_message)
                
                try:
                    # Final URL
                    url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
                    st.session_state.driver.get(url)
                    
                    # Page load hone ka wait (Isse kam mat karna)
                    time.sleep(22) 
                    
                    # Powerful Clicking Script (4 different methods)
                    click_script = """
                    var methods = [
                        () => document.querySelector('span[data-icon="send"]').parentElement.click(),
                        () => document.querySelector('button[aria-label="Send"]').click(),
                        () => { 
                            var event = new KeyboardEvent('keydown', {keyCode: 13, which: 13, bubbles: true});
                            document.querySelector('div[contenteditable="true"]').dispatchEvent(event);
                        },
                        () => document.querySelector('footer button').click()
                    ];
                    for (let m of methods) { try { m(); break; } catch(e) {} }
                    """
                    st.session_state.driver.execute_script(click_script)
                    
                    st.write(f"✅ {index+1}. Sent to: {phone}")
                except Exception as e:
                    st.write(f"❌ {index+1}. Failed for {phone}")
                
                # Progress and Delay
                progress_bar.progress((index + 1) / len(df))
                time.sleep(6) # Thoda gap taaki account safe rahe
            
            st.success("Saare 250 messages chale gaye! 🎉")

# Logout button
if st.button("Stop & Logout"):
    if st.session_state.driver:
        st.session_state.driver.quit()
        st.session_state.driver = None
        st.success("Session Closed.")
