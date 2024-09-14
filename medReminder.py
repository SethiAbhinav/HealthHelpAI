import streamlit as st
import pandas as pd
from PIL import Image
import hashlib
import sqlite3
from datetime import datetime, timedelta
import logging

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
    logger.debug("Session state initialized for user.")
if 'page' not in st.session_state:
    st.session_state.page = "login"
    logger.debug("Session state initialized for page.")

# Database setup
conn = sqlite3.connect('med_reminder.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS medications
             (id INTEGER PRIMARY KEY, username TEXT, name TEXT, dosage TEXT, time TEXT, stock INTEGER, next_dose DATETIME)''')
conn.commit()
logger.debug("Database tables created or checked.")

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
    logger.debug("Password hashed successfully.")

def authenticate(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    user = c.fetchone()
    if user:
        logger.info(f"User {username} authenticated successfully.")
    return user is not None

def register_user(username, password):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        logger.info(f"User {username} registered successfully.")
        return True
    except sqlite3.IntegrityError:
        logger.error(f"Failed to register user {username}. Username already exists.")
        return False

def save_medication(username, name, dosage, time, stock):
    next_dose = datetime.now().replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)
    if next_dose <= datetime.now():
        next_dose += timedelta(days=1)
    c.execute("INSERT INTO medications (username, name, dosage, time, stock, next_dose) VALUES (?, ?, ?, ?, ?, ?)",
              (username, name, dosage, time.strftime("%H:%M"), stock, next_dose))
    conn.commit()
    logger.info(f"Medication {name} saved for user {username}.")

def get_medications(username):
    c.execute("SELECT * FROM medications WHERE username=?", (username,))
    medications = c.fetchall()
    if medications:
        logger.info(f"Retrieved medications for user {username}.")
    return medications

def update_medication_stock(med_id, new_stock):
    c.execute("UPDATE medications SET stock = ? WHERE id = ?", (new_stock, med_id))
    conn.commit()
    logger.info(f"Stock updated for medication with ID {med_id}.")

def update_next_dose(med_id, next_dose):
    c.execute("UPDATE medications SET next_dose = ? WHERE id = ?", (next_dose, med_id))
    conn.commit()
    logger.info(f"Next dose updated for medication with ID {med_id}.")

def login_page():
    st.title("Med Reminder App")
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.user = username
            st.session_state.page = "home"
            st.rerun()
            logger.info(f"User {username} logged in successfully.")
        else:
            st.error("Invalid username or password")
            logger.error(f"Login attempt failed for user {username}.")

    st.write("Don't have an account?")
    if st.button("Register"):
        st.session_state.page = "register"
        st.rerun()
        logger.info(f"User {username} navigated to register page.")

def logout():
    st.session_state.user = None
    st.session_state.page = "login"
    st.success("Logged out successfully!")
    st.rerun()
    logger.info("User logged out successfully.")

def register_page():
    st.title("Med Reminder App")
    st.subheader("Register")
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    if st.button("Register"):
        if register_user(username, password):
            st.success("Registered successfully! Please log in.")
            st.session_state.page = "login"
            st.rerun()
            logger.info(f"User {username} registered successfully.")
        else:
            st.error("Username already exists")
            logger.error(f"Registration attempt failed for user {username}. Username already exists.")
    
    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()
        logger.info(f"User navigated back to login page from register page.")

def process_image(image):
    # This is a placeholder function for image processing
    st.write("Image processing for medication information extraction is not implemented in this example.")
    st.write("Please enter the medication information manually.")
    logger.info("Image processing not implemented. Manual input required.")
    return None, None, None

def input_selection_page():
    st.title("Add New Medication")
    st.write("Choose how you want to input your medication information:")
    
    if st.button("Upload Image"):
        st.session_state.page = "upload_image"
        st.rerun()
        logger.info("User selected to upload image for medication information.")
    
    if st.button("Fill Form"):
        st.session_state.page = "fill_form"
        st.rerun()
        logger.info("User selected to fill form for medication information.")
    
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()
        logger.info("User navigated back to home page from input selection.")

def upload_image_page():
    st.title("Upload Medication Image")
    
    uploaded_file = st.file_uploader("Upload a photo of your medication", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        med_name, dosage, dosage_time = process_image(image)
        
        # After processing, move to the form page to confirm or edit the information
        st.session_state.med_name = med_name
        st.session_state.dosage = dosage
        st.session_state.dosage_time = dosage_time
        st.session_state.page = "fill_form"
        st.rerun()
        logger.info("Image uploaded and processed for medication information.")
    
    if st.button("Back"):
        st.session_state.page = "input_selection"
        st.rerun()
        logger.info("User navigated back to input selection from upload image page.")

def fill_form_page():
    st.title("Enter Medication Information")
    
    med_name = st.text_input("Medication Name", value=st.session_state.get('med_name', ''))
    dosage = st.text_input("Dosage Quantity", value=st.session_state.get('dosage', ''))
    dosage_time = st.time_input("Dosage Time", value=st.session_state.get('dosage_time', datetime.now().time()))
    stock = st.number_input("Stock (number of tablets/doses)", min_value=0, step=1, value=0)
    
    if st.button("Save Medication"):
        save_medication(st.session_state.user, med_name, dosage, dosage_time, stock)
        st.success("Medication saved successfully!")
        st.session_state.page = "home"
        st.rerun()
        logger.info(f"Medication {med_name} saved for user {st.session_state.user}.")

    if st.button("Back"):
        st.session_state.page = "input_selection"
        st.rerun()
        logger.info("User navigated back to input selection from fill form page.")

def home_page():
    st.title(f"Welcome to Med Reminder, {st.session_state.user}!")
    
    if st.button("Logout"):
        logout()
        logger.info(f"User {st.session_state.user} logged out.")
    
    if st.button("Add New Medication"):
        st.session_state.page = "input_selection"
        st.rerun()
        logger.info(f"User {st.session_state.user} navigated to add new medication page.")
    
    st.header("Your Medications")
    medications = get_medications(st.session_state.user)
    if medications:
        for med in medications:
            med_id, _, name, dosage, time, stock, next_dose = med
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader(name)
                st.write(f"Dosage: {dosage}")
                st.write(f"Time: {time}")
            with col2:
                st.write(f"Stock: {stock}")
                new_stock = st.number_input(f"Update stock for {name}", min_value=0, value=stock, step=1, key=f"stock_{med_id}")
                if new_stock != stock:
                    update_medication_stock(med_id, new_stock)
                    st.success(f"Stock updated for {name}")
                    logger.info(f"Stock updated for {name} to {new_stock}.")
            with col3:
                st.write(f"Next dose: {next_dose}")
                if st.button(f"Take dose of {name}"):
                    if stock > 0:
                        new_stock = stock - 1
                        update_medication_stock(med_id, new_stock)
                        next_dose = datetime.strptime(str(next_dose), "%Y-%m-%d %H:%M:%S") + timedelta(days=1)
                        update_next_dose(med_id, next_dose)
                        st.success(f"Dose taken. Stock updated to {new_stock}")
                        logger.info(f"Dose taken for {name}. Stock updated to {new_stock}.")
                    else:
                        st.error("No stock left. Please refill your medication.")
                        logger.error(f"No stock left for {name}.")
            st.markdown("---")
    else:
        st.write("You haven't added any medications yet.")
        logger.info(f"No medications found for user {st.session_state.user}.")

def main():
    if st.session_state.user is None:
        if st.session_state.page == "login":
            login_page()
        elif st.session_state.page == "register":
            register_page()
    else:
        if st.session_state.page == "home":
            home_page()
        elif st.session_state.page == "input_selection":
            input_selection_page()
        elif st.session_state.page == "upload_image":
            upload_image_page()
        elif st.session_state.page == "fill_form":
            fill_form_page()

if __name__ == "__main__":
    main()