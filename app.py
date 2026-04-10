import streamlit as st
import pandas as pd
import time
import random
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# 1. Page Setup
st.set_page_config(page_title="WhatsApp Bulk Sender", page_icon="🚀")
st.title("🚀 1-Click WhatsApp Automator")
st.markdown("Bina kisi API charge ke apne Excel data se automatically WhatsApp messages bhejein.")

# 2. File Uploader
uploaded_file = st.file_uploader("Apni CSV file upload karein (Columns: Phone, Message)", type=["csv"])

if uploaded_file is not None:
    # Data ko read karna aur screen par dikhana
    df = pd.read_csv(uploaded_file)
    st.write("Aapka Data:")
    st.dataframe(df)

    st.warning("⚠️ Dhyan rahe: Start karne se pehle aapko WhatsApp Web par QR code scan karke login karna hoga.")
    
    # 3. Start Automation Button
    if st.button("Start Sending Messages"):
        st.info("Browser open ho raha hai... Please wait.")
        
        try:
            # Chrome Browser ko automatically setup aur open karna
            options = webdriver.ChromeOptions()
            # options.add_argument("--headless") # Agar aap browser hide karna chahte hain toh ise uncomment karein
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            # Pehle WhatsApp Web open karna login ke liye
            driver.get("https://web.whatsapp.com")
            st.success("Braking: Apna WhatsApp QR Code scan karein. System 20 seconds wait kar raha hai login hone ka...")
            time.sleep(20) # QR code scan karne ka time
            
            success_count = 0
            
            # 4. Har number par loop chalana aur message bhejna
            for index, row in df.iterrows():
                phone = str(row['Phone']).strip()
                message = str(row['Message']).strip()
                
                # Message ko URL format me convert karna
                encoded_message = urllib.parse.quote(message)
                
                # Direct us number ki chat open karne wala URL
                url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
                driver.get(url)
                
                # Chat load hone ka wait karna (10 seconds)
                time.sleep(10)
                
                try:
                    # Message type hone ke baad 'Enter' dabane ka action
                    # WhatsApp update hota rehta hai, Enter key sabse safe approach hai
                    active_element = driver.switch_to.active_element
                    active_element.send_keys(Keys.ENTER)
                    
                    success_count += 1
                    st.write(f"✅ Message sent to {phone}")
                    
                except Exception as e:
                    st.error(f"❌ Failed to send to {phone}. Error: {e}")
                
                # 5. Account Block se bachne ke liye Random Delay (Bahut Zaroori)
                delay = random.randint(15, 30) # 15 se 30 seconds ke beech random gap
                st.write(f"⏳ Waiting {delay} seconds to avoid ban...")
                time.sleep(delay)
            
            st.success(f"🎉 Process Complete! Total {success_count} messages sent.")
            driver.quit() # Kaam khatam hone ke baad browser band karna
            
        except Exception as e:
            st.error(f"Ek error aayi hai: {e}")
