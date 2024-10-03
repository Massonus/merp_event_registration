# MERP Event Registration

This project is a web application for event registration, implemented using Flask and SQLAlchemy. Users can register for events, and administrators can manage them.

## Installation and Setup

## 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/Massonus/merp_event_registration.git
cd merp_event_registration
```

## 2. Create and Activate a Virtual Environment

### For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```
## 3. Install Dependencies
   Install the required dependencies:

```bash
pip install -r requirements.txt
```

## 4. Create a .env File
Create a .env file in the root directory of the project and add the following lines:

```bash
DATABASE_URL=postgresql+psycopg2://postgres:root@localhost:5432/Merp
SECRET_KEY=secret
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin
```

Note:

Ensure that your PostgreSQL database is named Merp.
The database user should be postgres, and the password should be root.

## 5. Initialize the Database
Run the following commands to set up the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 6. Run the Application
Start the application using the following command:
```bash
flask run
```

## 7. Open the Application in a Browser
Open your browser and go to the following address:
```bash
http://127.0.0.1:5000
```

## 9. Admin User Credentials
To log in to the admin panel, use the following credentials:
#### Email: admin@example.com
#### Password: admin

# OR
## Docker Setup
#### You can also run the application using docker-compose.yml. If you prefer, you can follow these steps to set up the application with Docker:
1. Build and start the containers:

```bash
docker-compose up --build
```
2. Access the application at:
```bash
http://localhost
```

## Additionally, you can view the already running application at the following link:

http://ec2-18-199-236-18.eu-central-1.compute.amazonaws.com