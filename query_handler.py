import sqlite3
import logging
import together
import streamlit as st

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Together.ai API
together_client = together.Together(api_key='63f7c168bb7791313bf41a29c742dbf3ca9d5930ff1bab9ba4f3b9a7aeb25c10')


# Database setup
conn = sqlite3.connect('med_reminder.db')
c = conn.cursor()

def fetch_user_data(username):
    conn = sqlite3.connect('med_reminder.db')
    c = conn.cursor()
    c.execute("SELECT name, dob, phone, diseases FROM users WHERE username=?", (username,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        logger.info(f"Fetched data for user {username}.")
    return user_data


def fetch_medication_data(username):
    conn = sqlite3.connect('med_reminder.db')
    c = conn.cursor()
    c.execute("SELECT name, dosage, time, stock, next_dose FROM medications WHERE username=?", (username,))
    medications = c.fetchall()
    conn.close()
    if medications:
        logger.info(f"Fetched medication data for user {username}.")
    return medications


def generate_response(user_data, medications, query):
    name, dob, phone, diseases = user_data
    medication_info = "\n".join([f"Medication: {med[0]}, Dosage: {med[1]}, Time: {med[2]}, Stock: {med[3]}, Next Dose: {med[4]}" for med in medications])
    prompt = f"User details:\nName: {name}\nDate of Birth: {dob}\nPhone: {phone}\nDiseases: {diseases}\n\nMedications:\n{medication_info}\n\nQuery: {query}\n\nProvide a concise response considering the user's health conditions and medications. Answer only in first person. Make it friendly and personalized."
    
    response = together_client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content


def query_page():
    st.title("Health Query")
    st.write("Ask any health-related question, and we'll provide an answer based on your health data.")
    
    query = st.text_area("Enter your query here:")
    
    if st.button("Submit"):
        if 'user' in st.session_state and st.session_state.user:
            user_data = fetch_user_data(st.session_state.user)
            medications = fetch_medication_data(st.session_state.user)
            if user_data and medications:
                response = generate_response(user_data, medications, query)
                st.write("Response:")
                st.write(response)
            else:
                st.error("User data or medication data not found.")
        else:
            st.error("You need to be logged in to ask a query.")

def main():
    if 'user' not in st.session_state or st.session_state.user is None:
        st.error("Please log in to use the query feature.")
    else:
        query_page()

if __name__ == "__main__":
    main()