

#  STEI Workshop Management — FastAPI Backend

A complete backend platform for managing **workshops, batches, students, clarity calls, categories, quotes, resources, assignments**, and authentication for both **Admins & Students**.
Built using **FastAPI + MySQL + JWT Auth**.

This system supports:
 Admin Portal
 Student Portal
 Google + Microsoft Login
 Clarity Calls (Admin + Student workflows)
 Assignments
 Resource Sharing
 Workshop & Batch Scheduling

---

##  Features Overview

### Authentication

* Student login + registration
* Admin login
* Secure JWT-based authorization
* Google OAuth login
* Microsoft OAuth login
* OTP email flow
* Logout

---

### 🧑‍🎓 Student Features

* Student registration
* Profile update
* Profile completion tracking
* Dashboard
* Workshop/Batch enrollments
* View resources (when profile complete)
* Clarity call questionnaire (MCQ)
* View clarity call status + history
* Cleanup incomplete assignments

---

### 🧑‍💼 Admin Features

* Admin dashboard (revenue, workshop, batch stats)
* Student management (CRUD)
* Workshop management (CRUD)
* Batch management (CRUD)
* Category management (CRUD)
* Quotes management (CRUD)
* Clarity call management (CRUD)
* Student assignments creation
* Resource management (CRUD)

---

##  Tech Stack

| Component | Tech                |
| --------- | ------------------- |
| Language  | Python 3.10+        |
| Framework | FastAPI             |
| Database  | MySQL               |
| ORM       | Raw SQL             |
| Auth      | JWT                 |
| Email     | SMTP via send_email |
| OAuth     | Google + Microsoft  |
| Server    | Uvicorn             |

---

##  Project Structure

```
STEI-Workshop-Management/
│
├── Admin/
│   ├── admin_dashboard.py        # Dashboard stats: revenue, workshops, batches
│   ├── batches.py                # Admin batch CRUD
│   ├── categories.py             # Admin categories CRUD
│   ├── clarity_call.py           # Admin clarity-call CRUD
│   ├── quote.py                  # Admin quotes CRUD
│   ├── resources_student.py      # Admin resource mgmt
│   ├── students.py               # Admin student mgmt CRUD
│   └── workshops.py              # Admin workshop CRUD
│
├── auth/
│   ├── jwt/
│   │   ├── jwt_auth.py           # JWT auth helpers
│   │   └── password_auth.py      # Password hashing
│   ├── Login_Logout/
│   │   ├── login.py              # All logins
│   │   └── logout.py             # Logout
│   ├── Google_Login/
│   │   └── oauth_google.py       # Google OAuth
│   ├── Microsoft_Login/
│   │   └── oauth_microsoft.py    # Microsoft OAuth
│   └── OTP/
│       ├── otp_auth.py           # OTP verify
│       └── send_email.py         # Email sender
│
├── Students/
│   ├── clarity_call.py           # Pre-call Q/A + history
│   ├── enrollments.py            # Workshop/Batch enroll
│   ├── resources.py              # View resources
│   ├── student_dashboard.py      # Dashboard
│   ├── student_update.py         # Student profile update
│   └── student.py                # Student create + profile stats
│
├── database/
│   ├── Database.sql              # SQL schema
│   ├── Database Connection Diagram.png
│   └── db.py                     # DB connection
│
├── main.py                       # FastAPI entry
├── config.py                     # DB config env settings
├── .env                          # Env vars
├── requirements.txt              # Dependencies
├── README.md
└── .gitignore
```

---

##  Database Setup

1. Create database

```sql
CREATE DATABASE stei;
```

2. Run schema

```bash
mysql -u root -p stei < Database.sql
```

3. Configure DB
   `config.py`

```python
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD",
    "database": "stei"
}
```

---

##  Install & Run

### 1) Clone

```
git clone https://github.com/kartik-mone/STEI-Workshop-Management-
cd STEI-Workshop-Management
```

### 2) Create venv

```
python -m venv venv
source venv/bin/activate   # mac/linux
venv\Scripts\activate      # windows
```

### 3) Install dependencies

```
pip install -r requirements.txt
```

### 4) Start server

```
uvicorn main:app --reload
```

### Docs:

* Swagger → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* ReDoc → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

##  Major API Endpoints

> Only key highlights — each module has many.

### Auth

| Method | Route               |
| ------ | ------------------- |
| POST   | /auth/student/login |
| POST   | /auth/admin/login   |
| POST   | /auth/google        |
| POST   | /auth/microsoft     |
| POST   | /auth/otp           |
| POST   | /auth/logout        |

---

### Students

| Method | Route                                              |
| ------ | -------------------------------------------------- |
| POST   | /student/register                                  |
| GET    | /student/dashboard/profile                         |
| GET    | /student/dashboard/profile_completion              |
| PUT    | /auth/student/update                               |
| GET    | /student/clarity_call/precall_questionnaire        |
| POST   | /student/clarity_call/submit_precall_questionnaire |
| GET    | /student/clarity_call/history                      |

---

###  Admin

| Method | Route                           |
| ------ | ------------------------------- |
| GET    | /admin-dashboard/               |
| POST   | /admin/students/register        |
| PUT    | /admin/students/update/{id}     |
| DELETE | /admin/students/delete/{id}     |
| POST   | /admin/clarity_call/create      |
| PUT    | /admin/clarity_call/update/{id} |
| DELETE | /admin/clarity_call/delete/{id} |

---

###  Workshops & Batches

| Method | Route                                  |
| ------ | -------------------------------------- |
| POST   | /workshops/add                         |
| PUT    | /workshops/update/{id}                 |
| DELETE | /workshops/delete/{id}                 |
| POST   | /enrollments/enroll/{workshop}/{batch} |

---

###  Resources

| Method | Route                       |
| ------ | --------------------------- |
| POST   | /auth/resources/create      |
| PUT    | /auth/resources/update/{id} |
| DELETE | /auth/resources/delete/{id} |
| GET    | /auth/resources             |
| GET    | /auth/resources/categories  |

---

##  Clarity Call Workflow

### Student

1. View status → `/student/clarity_call/clarity_call_status`
2. View questions → `/student/clarity_call/precall_questionnaire`
3. Submit MCQ → `/student/clarity_call/submit_precall_questionnaire`
4. History → `/student/clarity_call/history`

### Admin

* Create, update, delete clarity calls
* View call history
* Assign calls to student + mentor

---

##  OAuth — Google & Microsoft

### Google OAuth

```
POST /auth/google/login
```

Handles:

* Code exchange
* Identity token validation
* Auto-register + login
* Returns JWT

### Microsoft OAuth

```
POST /auth/microsoft/login
```

Similar process using Microsoft identity endpoint.

Both fallback to:

* Create student if new
* Generate JWT token

---

##  Requirements

```
fastapi
uvicorn[standard]
pydantic
pydantic[email]
pymysql
python-dotenv
PyJWT
cryptography
python-jose
passlib
requests
```

---

##  Future Improvements

* Fetch overall analytics
* Handle clarity call payment 
* Add password reset

---

##  License

Private / Internal project

