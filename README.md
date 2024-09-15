# MedReminder

## Overview
MedReminder is a simple and effective web application designed to help users keep track of their medications. It allows users to log in, register, and manage their medication schedules, including adding, updating, and deleting medications. The application also supports image uploads for prescription recognition and integrates with MindsDB for health queries. The user receives a WhatsApp message as a reminder to take his medicine dose.

## Features
- User authentication (login and registration)
- Medication management (add, update, delete)
- Upload prescription images for automatic medication and dosage extraction
- Health query feature powered by AI
- User-friendly interface built with Streamlit

<img width="943" alt="Screenshot 2024-09-16 at 5 02 30 AM" src="https://github.com/user-attachments/assets/635c225e-7a3b-46ca-9fc6-ae5038638688">

## Technologies Used
- **Frontend**: Streamlit
- **Backend**: SQLite for database management
- **Image Processing**: PIL for image handling
- **AI Integration**: Upstage's Document parser for prescription reading.
- **AI Integration**: Together.ai for using Meta-Llama-3.1 to extract key information from the prescription's parsed data.
- **Logging**: Python's built-in logging module
<img width="879" alt="Screenshot 2024-09-16 at 5 03 56 AM" src="https://github.com/user-attachments/assets/4601c651-a9ab-4daa-8011-d89a69a73dd6">

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/SethiAbhinav/HealthHelpAI
   cd MedReminder
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run medReminder.py
   ```

## Usage
- **Register**: Create a new account by providing a username, password, name, date of birth, phone number, and any diseases.
- **Login**: Access your account using your username and password.
- **Manage Medications**: Add new medications by filling out a form or automate it by uploading an image of your prescription.
- **Health Queries**: Get your health-related questions answered based on your medication and health profile.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Thanks to the developers of Streamlit, Together.ai, and MindsDB for their amazing tools and libraries.
