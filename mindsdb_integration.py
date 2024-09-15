import mindsdb_sdk
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import logging

TWILIO_WHATSAPP = '+14155238886'

# Logging setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MindsDB connection setup
server = mindsdb_sdk.connect('http://127.0.0.1:47334')
try:
    project = server.get_project('health_query')
except:
    project = server.create_project('health_query')

def setup_mindsdb():
    try:
        cnx = sqlite3.connect('med_reminder.db')
        user_metadata_df = pd.read_sql_query("SELECT u.username as username, u.phone as phone, m.next_dose as next_dose, m.name as medication_name, m.stock as stock FROM users u LEFT JOIN medications m ON u.username = m.username where next_dose IS NOT NULL", cnx)
        files_db = server.get_database('files')
        table_name = 'med_reminder'
        try: 
            logger.debug('getting table')
            med_reminder_table = files_db.get_table(table_name).fetch()
            files_db.tables.drop(table_name)
            logger.debug("Table 'med_reminder' gotten successfully.")
        except:
            pass
        med_reminder_table = files_db.create_table('med_reminder', user_metadata_df)
        my_table = files_db.query('SELECT * FROM files.med_reminder where next_dose IS NOT NULL').fetch()
        valid_users = my_table.dropna(subset=['phone', 'medication_name']).to_dict(orient='records')
        print("Valid Users", valid_users)

        for user in valid_users:
            try: 
                phone_str = str(user['phone'])
                name = user['username']
                phone_number = phone_str[2:] if phone_str.startswith("91") else phone_str
                medication = user['medication_name']
                next_dose_time = user['next_dose']
                medication_stock = user['stock']

                # Check if next_dose_time is within 15 minutes
                next_dose_time = datetime.strptime(next_dose_time, '%Y-%m-%d %H:%M:%S')  # Convert string to datetime
                if (next_dose_time - datetime.now()).total_seconds() < 900:  # 15 minutes = 900 seconds
                    reminder_message = f"Please take 1 dose of {medication} at {next_dose_time}, as prescribed.\n\nYour current stock is {medication_stock}.\nHave a good day :D"
                    print("crossed")
                    job_name = f'remind_dosage_{name}_{medication}'
                    try:
                        logger.info('getting job')
                        project.get_job(job_name)
                        logger.info('Got job')
                    except: 
                        logger.info('creating job')
                        project.create_job(
                                job_name,
                                f"INSERT INTO whatsapp_bot.messages (body, from_number, to_number) VALUES('{reminder_message}', 'whatsapp:{TWILIO_WHATSAPP}', 'whatsapp:+91{phone_number}')",
                                repeat_str = '1 month'
                            )
                        logger.info('Created job')
            except:
                logger.info("Data issue was there.")
    except Exception as e:
        logger.error(f"Error setting up MindsDB: {str(e)}")

if __name__ == "__main__":
    setup_mindsdb()