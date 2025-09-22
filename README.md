# STEI Workshop Management - FastAPI

A Workshop Management System built with **FastAPI**, designed to manage workshops, batches, students, categories, quotes, and authentication for both **Admins** and **Students**.
This project provides a structured backend API with **JWT authentication** for secure role-based access.

---

## Features

* **Authentication**

  * Student & Admin login with JWT (`Login/login.py`)
  * Student & Admin role-based routes (`auth.py`)

* **Admin Dashboard**

  * Manage students, workshops, batches, categories, and quotes (`routes/admin_dashboard.py`)

* **Student Features**

  * Student profile & updates (`Students/student.py`, `Students/student_update.py`)
  * Enrollments in workshops & batches (`Students/enrollments.py`)
  * Student dashboard (`Students/student_dashboard.py`)
  * Logout (`Students/logout.py`)

* **Workshop Management**

  * Add, update, delete, and fetch workshops (`routes/workshops.py`)

* **Batch Management**

  * Manage workshop batches (`routes/batches.py`)

* **Categories**

  * Manage categories (`routes/categories.py`)

* **Quotes**

  * Manage motivational quotes (`routes/quote.py`)

* **Database**

  * MySQL database integration (`db.py` and `Database.sql`)

---

## Project Structure

```bash
STEI WORKSHOP MANAGEMENT - FASTAPI
│── Login/
│   └── login.py                 # Handles login logic
│
│── routes/
│   ├── admin_dashboard.py       # Admin-specific operations
│   ├── batches.py               # Endpoints for batch operations
│   ├── categories.py            # Endpoints for categories
│   ├── quote.py                 # Endpoints for quotes
│   ├── students.py              # Endpoints for student management (admin-side)
│   └── workshops.py             # Endpoints for workshops
│
│── Students/
│   ├── enrollments.py           # Student enrollments in workshops/batches
│   ├── logout.py                # Student logout
│   ├── student_dashboard.py     # Student dashboard view
│   ├── student_update.py        # Student profile update
│   └── student.py               # Student profile
│
│── auth.py                      # Authentication & authorization (JWT helpers)
│── config.py                    # DB config (MySQL settings)
│── db.py                        # DB connection
│── Database.sql                 # SQL schema
│── Database Connection Diagram.png  # ER diagram
│── requirements.txt             # Dependencies
│── Commands.txt                 # Helpful commands
│── main.py                      # FastAPI entry point
│── .gitignore
│── README.md
```

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-username/stei-workshop-management.git
cd stei-workshop-management
```

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

---

## Database Setup

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

---

## Run the Server

```bash
uvicorn main:app --reload
```

API available at:
`http://127.0.0.1:8000`
Swagger UI: `http://127.0.0.1:8000/docs`

---

## API Endpoints

### Authentication

* `POST /auth/student/login` → Student login
* `POST /auth/admin/login` → Admin login
* `GET /auth/student/profile` → Student profile
* `GET /auth/admin/profile` → Admin profile
* `POST /students/logout` → Student logout

### Students

* `POST /students/register` → Register new student
* `GET /students/` → Get all students (admin only)
* `GET /students/{id}` → Get student by ID
* `PUT /students/{id}` → Update student info
* `DELETE /students/{id}` → Delete student
* `GET /students/dashboard` → Student dashboard
* `POST /students/enroll` → Enroll student in a workshop/batch

### Workshops

* `POST /workshops/add` → Add workshop (admin only)
* `GET /workshops/` → List workshops
* `PUT /workshops/{id}` → Update workshop (admin only)
* `DELETE /workshops/{id}` → Delete workshop (admin only)

### Batches

* `POST /batches/add` → Add batch (admin only)
* `PUT /batches/{id}` → Update batch (admin only)

### Categories

* `POST /categories/add` → Add category (admin only)
* `GET /categories/` → Get all categories
* `GET /categories/{id}` → Get specific category
* `PUT /categories/{id}` → Update category (admin only)
* `DELETE /categories/{id}` → Delete category (admin only)

### Quotes

* `POST /quotes/add` → Add quote (admin only)
* `GET /quotes/` → Get all quotes
* `GET /quotes/{id}` → Get specific quote
* `PUT /quotes/{id}` → Update quote (admin only)
* `DELETE /quotes/{id}` → Delete quote (admin only)

---

## Tech Stack

* Python 3.10+
* FastAPI
* MySQL
* Pydantic
* Uvicorn
* PyMySQL
* JWT Authentication

