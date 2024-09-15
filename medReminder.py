import streamlit as st
import pandas as pd
from PIL import Image
import hashlib
import sqlite3
from datetime import datetime, timedelta
import logging
from mindsdb_integration import setup_mindsdb

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = "login"

# Database setup
conn = sqlite3.connect('med_reminder.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, 
              password TEXT,
              name TEXT,
              dob DATE,
              phone TEXT,
              diseases TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS medications
             (id INTEGER PRIMARY KEY, username TEXT, name TEXT, dosage TEXT, time TEXT, stock INTEGER, next_dose DATETIME)''')
conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    return c.fetchone()

def register_user(username, password, name, dob, phone, diseases):
    try:
        c.execute("INSERT INTO users (username, password, name, dob, phone, diseases) VALUES (?, ?, ?, ?, ?, ?)", 
                  (username, hash_password(password), name, dob, phone, diseases))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def save_medication(username, name, dosage, time, stock):
    next_dose = datetime.now().replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)
    if next_dose <= datetime.now():
        next_dose += timedelta(days=1)
    c.execute("INSERT INTO medications (username, name, dosage, time, stock, next_dose) VALUES (?, ?, ?, ?, ?, ?)",
              (username, name, dosage, time.strftime("%H:%M"), stock, next_dose))
    conn.commit()

def get_medications(username):
    c.execute("SELECT * FROM medications WHERE username=?", (username,))
    return c.fetchall()

def update_medication_stock(med_id, new_stock):
    c.execute("UPDATE medications SET stock = ? WHERE id = ?", (new_stock, med_id))
    conn.commit()
   
def update_next_dose(med_id, next_dose):
    c.execute("UPDATE medications SET next_dose = ? WHERE id = ?", (next_dose, med_id))
    conn.commit()

def login_page():
    st.title("Med Reminder App")
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state.user = username
            st.session_state.name = user[2]
            st.session_state.dob = user[3]
            st.session_state.phone = user[4]
            st.session_state.diseases = user[5]
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
    name = st.text_input("Name", key="register_name")
    dob = st.date_input("Date of Birth", key="register_dob")
    phone = st.text_input("Phone Number", key="register_phone")
    diseases = st.text_area("Diseases", key="register_diseases")
    
    if st.button("Register"):
        if register_user(username, password, name, dob, phone, diseases):
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
    is_valid = True
    if st.button("Save Medication"):
        # Validation checks
        if not med_name:
            st.error("Medication name is required.")
            logger.error("Validation error: Medication name is required.")
            is_valid = False
        
        if not dosage:
            st.error("Dosage quantity is required.")
            logger.error("Validation error: Dosage quantity is required.")
            is_valid = False
        
        if stock < 0:
            st.error("Stock cannot be negative.")
            logger.error("Validation error: Stock cannot be negative.")
            is_valid = False
        
        if is_valid:
            save_medication(st.session_state.user, med_name, dosage, dosage_time, stock)
            st.success("Medication saved successfully!")
            st.session_state.page = "home"
            setup_mindsdb()
            logger.info(f"Medication {med_name} saved for user {st.session_state.user}.")
            st.rerun()

    if st.button("Back"):
        st.session_state.page = "input_selection"
        st.rerun()
        logger.info("User navigated back to input selection from fill form page.")

def delete_medication(med_id):
    c.execute("DELETE FROM medications WHERE id = ?", (med_id,))
    conn.commit()
    logger.info(f"Medication with ID {med_id} deleted.")

def home_page():
    st.title(f"Welcome to Med Reminder, {st.session_state.name}!")
    st.write(f"Date of Birth: {st.session_state.dob}")
    st.write(f"Phone Number: {st.session_state.phone}")
    st.write(f"Diseases: {st.session_state.diseases}")
    
    if st.button("Logout"):
        logout()
        logger.info(f"User {st.session_state.user} logged out.")
    
    if st.button("Add New Medication"):
        st.session_state.page = "input_selection"
        st.rerun()
        logger.info(f"User {st.session_state.user} navigated to add new medication page.")
    
    if st.button("Ask a Health Query"):
        st.session_state.page = "query"
        st.rerun()
        logger.info(f"User {st.session_state.user} navigated to query page.")

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
            if st.button(f"Delete {name}", key=f"delete_{med_id}"):
                delete_medication(med_id)
                st.success(f"{name} has been deleted.")
                st.rerun()
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
        elif st.session_state.page == "query":
            import query_handler
            query_handler.main()

if __name__ == "__main__":
    main()