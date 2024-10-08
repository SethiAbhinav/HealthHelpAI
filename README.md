# HealthHelpAI

## Overview
HealthHelpAI is a user-friendly web application designed to help users manage and track their medication schedules with ease. The app provides key features such as automatic prescription analysis and personalized health query responses powered by AI. Additionally, users receive timely WhatsApp reminders for their medications, ensuring they never miss a dose.

## Features
- User Authentication: Register and log in securely with personalized profiles.
- Medication Management: Easily add, update, or delete medications.
- Prescription Upload: Upload prescription images to automatically extract medication details and dosages using AI.
- AI-Powered Health Queries: Get personalized answers to health-related queries based on user data.
- WhatsApp Reminders: Receive automated medication reminders via WhatsApp 15 minutes before each dose.
- Streamlined Interface: Simple and intuitive UI built using Streamlit for seamless interaction.
  
<img width="875" alt="Screenshot 2024-09-16 at 5 42 10 AM" src="https://github.com/user-attachments/assets/04af3867-79c8-480c-bfad-0267d4410ad6">

## Technologies Used
- **Frontend**: Streamlit
- **Backend**: SQLite for efficient and lightweight database management.
- **AI Integration**:
-    Upstage's Document parser for prescription reading.
-    Together.ai: Utilizes LLM's to process and extract information from prescription data and answer user health queries.
- **Logging**: Python's built-in logging module
<img width="704" alt="Screenshot 2024-09-16 at 6 01 52 AM" src="https://github.com/user-attachments/assets/6e41d020-1828-45f2-b18f-9c0ecff47c12">


<img width="879" alt="Screenshot 2024-09-16 at 5 03 56 AM" src="https://github.com/user-attachments/assets/4601c651-a9ab-4daa-8011-d89a69a73dd6">

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/SethiAbhinav/HealthHelpAI
   cd HealthHelpAI
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run healthHelpAI.py
   ```

## Usage
- **Register**: Sign up by providing personal details such as username, password, date of birth, phone number, and any existing medical conditions.
- **Login**: Access your account using your username and password.
- **Manage Medications**: Add new medications by filling out a form or automate it by uploading an image of your prescription.
- **Health Queries**: Get your health-related questions answered based on your medication and health profile.
- **WhatsApp Reminders**: Get notified via WhatsApp 15 minutes before your scheduled medication doses.

## Contributing
We welcome contributions! If you have any ideas, find bugs, or want to enhance the app, feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Thanks to the developers of Streamlit, Together.ai, Upstage and MindsDB for their amazing tools and libraries.
