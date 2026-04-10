import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time
import pandas as pd
import os

# Page Config
st.set_page_config(page_title="Het's Ultimate Cloud Bot", layout="wide")
st.title("🚀 Het's WhatsApp Automation (Cloud Version)")

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

# --- UI Side ---
col1, col2 = st.columns(2)

with col1:
    st.header("Step 1: Login")
    if st.button("Generate QR Code"):
        st.session_state.driver = setup_driver()
        st.session_state.driver.get("https://web.whatsapp.com")
        with st.spinner("Loading WhatsApp Web... (30 sec)"):
            time.sleep(35)
            st.session_state.driver.save_screenshot("qr.png")
            st.image("qr.png", caption="Scan QR from Mobile")

with col2:
    st.header("Step 2: Sending")
    if st.button("Start Bulk Sending"):
        if not st.session_state.driver:
            st.error("Pehle QR scan karein!")
        elif not os.path.exists("leads.csv"):
            st.error("leads.csv file nahi mili!")
        else:
            df = pd.read_csv("leads.csv")
            st.info(f"Processing {len(df)} contacts...")
            progress = st.progress(0)
            
            for index, row in df.iterrows():
                phone = str(row['Phone']).replace("+", "").strip()
                message = row['Message']
                
                try:
                    # Link Open
                    url = f"https://web.whatsapp.com/send?phone={phone}&text={message}"
                    st.session_state.driver.get(url)
                    
                    # Wait for Send Button to appear
                    time.sleep(15) 
                    
                    # 4-Method Click Logic
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
                    
                    st.write(f"✅ {index+1}. Sent to {phone}")
                except Exception as e:
                    st.write(f"❌ {index+1}. Failed {phone}")
                
                progress.progress((index + 1) / len(df))
                time.sleep(5) # Delay to avoid ban
            
            st.success("Sabb kaam ho gaya! PC band kar sakte ho. 🎉")

if st.button("Stop & Close"):
    if st.session_state.driver:
        st.session_state.driver.quit()
        st.session_state.driver = None
        st.success("Stopped.")
