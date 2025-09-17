
# STEI Workshop Management - FastAPI

A Workshop Management System built with **FastAPI**, designed to manage workshops, batches, students, categories, and quotes.  
This project provides a structured backend API for workshop administration.


## Features
- **User Authentication**
  - Login endpoint (`login.py`)

- **Workshop Management**
  - Add, update, delete, and fetch workshops (`routes/workshops.py`)

- **Batch Management**
  - Manage workshop batches (`routes/batches.py`)

- **Student Management**
  - Register, update, delete students with enrollment info (`routes/students.py`)

- **Categories**
  - Manage categories (`routes/categories.py`)

- **Quotes**
  - Manage motivational quotes (`routes/quote.py`)

- **Database**
  - MySQL database integration (`db.py` and `Database.sql`)


##  Project Structure

```bash
STEI WORKSHOP MANAGEMENT - FASTAPI
│── Login/
│   └── login.py
│
│── routes/
│   ├── batches.py
│   ├── categories.py
│   ├── quote.py
│   ├── students.py
│   └── workshops.py
│
│── STEI/                      # Virtual environment (ignored in Git)
│── config.py                   # DB config (ignored in Git)
│── db.py                       # DB connection
│── Database.sql                # SQL schema
│── requirements.txt            # Dependencies
│── Commands.txt                # Helpful commands
│── Database Connection Diagram.png
│── main.py                     # FastAPI entry point
│── .gitignore
│── README.md
```

##  Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/stei-workshop-management.git
cd stei-workshop-management
````

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # On Windows
# OR
source venv/bin/activate  # On Linux/Mac
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```



##  Database Setup

1. Install MySQL and create a database.
2. Import the schema:

```bash
mysql -u root -p your_db_name < Database.sql
```

3. Configure `config.py` with your MySQL credentials:

```python
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "stei"
}

```



##  Run the Server

```bash
uvicorn main:app --reload
```

By default, the API runs on:
 `http://127.0.0.1:8000`



##  API Endpoints

### Students

* `POST /students/register` → Register new student
* `GET /students/` → Get all students
* `GET /students/{id}` → Get student by ID
* `PUT /students/{id}` → Update student info
* `DELETE /students/{id}` → Delete student

### Workshops

* `POST /workshops/add` → Add workshop
* `GET /workshops/` → List workshops
* `PUT /workshops/{id}` → Update workshop
* `DELETE /workshops/{id}` → Delete workshop

### Batches

* `POST /batches/add` → Add batch
* `PUT /batches/{id}` → Update batch

### Categories

* `POST /categories/add` → Add category
* `GET /categories/` → Get all categories

### Quotes

* `POST /quotes/add` → Add quote
* `GET /quotes/` → Get all quotes
* `PUT /quotes/{id}` → Update quote
* `DELETE /quotes/{id}` → Delete quote



## Tech Stack

* **Python 3.10+**
* **FastAPI**
* **MySQL**
* **Pydantic**
* **Uvicorn**
* **PyMySQL**


