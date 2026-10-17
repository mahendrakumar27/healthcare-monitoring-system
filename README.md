# Satara District Healthcare Portal (Student PBL Prototype)

A Flask + SQLite prototype with a public directory of government healthcare facilities and a separate officials dashboard.

## Features
- Public homepage with search by facility/taluka and filter by facility type.
- 80+ PHC names and talukas seeded from the Zilla Parishad Satara PHC directory, plus a small number of government hospital entries.
- Facility details page with sample bed counts, services, departments, doctor names/specializations, opening hours, emergency status, medicine status, and map search link.
- Doctors' phone numbers are not displayed.
- Officials login and facility add/edit/delete tools.
- SQLite database created automatically as `healthcare.db`.

## Important data note
The PHC names and talukas are based on the official directory: https://www.zpsatara.gov.in/en/satara-district-primary-health-centers-phcs-list/

The added hospital entries and all resource details (beds, staff, medicines, hours, doctors, departments and services) are demonstration/sample data unless independently verified. Doctor names are deliberately labelled `Sample Doctor`; do not use this prototype to make real care decisions or present sample information as verified.

## Run on Windows
1. Install Python 3.10 or newer.
2. Extract the ZIP folder.
3. Open Command Prompt/Terminal inside the extracted folder.
4. Create a virtual environment:
   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   ```
5. Install requirements:
   ```bat
   pip install -r requirements.txt
   ```
6. Run the app:
   ```bat
   python app.py
   ```
7. Open http://127.0.0.1:5000 in your browser.

## Demo officials login
- Username: `admin`
- Password: `admin123`

For any deployment beyond a classroom demo, set environment variables `SECRET_KEY`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD`; use a proper authentication system and HTTPS. Do not expose the development server publicly.

## Reset the sample database
Stop the app, delete `healthcare.db`, and run `python app.py` again. The database and sample rows will be recreated automatically.
