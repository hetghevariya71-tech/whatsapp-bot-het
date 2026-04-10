import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time
import pandas as pd
import os

# Page Configuration
st.set_page_config(page_title="Het's Cloud Bot", layout="centered")
st.title("📲 Het's WhatsApp Training Bot")
st.write("PC band karke bhi messages bhejte rahiye!")

# --- Selenium Setup Function ---
def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Bina window ke chalega
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # Cloud ke liye special user agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    # Chromium ka binary path (Streamlit Cloud default)
    options.binary_location = "/usr/bin/chromium"

    try:
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        st.error(f"Driver setup error: {e}")
        return None

# --- Session State to keep driver alive ---
if 'driver' not in st.session_state:
    st.session_state.driver = None

# --- Step 1: QR Code Generation ---
st.header("Step 1: Login")
if st.button("Generate QR Code"):
    if st.session_state.driver is None:
        st.session_state.driver = setup_driver()
    
    if st.session_state.driver:
        st.session_state.driver.get("https://web.whatsapp.com")
        with st.spinner("QR Code load ho raha hai... 30 seconds wait karein"):
            time.sleep(30)  # WhatsApp Web load hone mein time leta hai
            st.session_state.driver.save_screenshot("qr_code.png")
            st.image("qr_code.png", caption="Apne phone se scan karein")
            st.success("Agar scan ho gaya hai, toh Step 2 par jayein.")

# --- Step 2: Message Sending ---
st.header("Step 2: Sending")
if st.button("Start Automation"):
    if st.session_state.driver is None:
        st.error("Pehle Step 1 karke QR scan karein!")
    else:
        if os.path.exists("leads.csv"):
            df = pd.read_csv("leads.csv")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, row in df.iterrows():
                phone = str(row['Phone']).replace("+", "").strip()
                # Gujarati message support ke liye encoding
                message = row['Message']
                
                try:
                    # Direct Link method
                    url = f"https://web.whatsapp.com/send?phone={phone}&text={message}"
                    st.session_state.driver.get(url)
                    time.sleep(15)  # Wait for page to load
                    
                    # Enter dabane ka jugaad (Cloud par direct keys kabhi kabhi nahi chalti)
                    # Isliye hum link open karke 15 sec wait karte hain
                    
                    status_text.text(f"Processing: {phone} ({index+1}/{len(df)})")
                    progress_bar.progress((index + 1) / len(df))
                    st.write(f"✅ Attempted: {phone}")
                    
                except Exception as e:
                    st.write(f"❌ Error with {phone}: {e}")
                
                time.sleep(5)  # Chota delay next message se pehle
            
            st.success("Automation Process Complete! 🎉")
        else:
            st.error("leads.csv file nahi mili! Check karein GitHub par upload ki hai ya nahi.")

# --- Logout/Close Button ---
if st.button("Close Browser Session"):
    if st.session_state.driver:
        st.session_state.driver.quit()
        st.session_state.driver = None
        st.success("Session closed.")
