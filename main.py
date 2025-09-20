from fastapi import FastAPI

# Admin Routes 
from routes.categories import router as categories_router
from routes.workshops import workshops_router
from routes.batches import batches_router
from routes.students import students_router_admin
from routes.quote import quotes_router
from routes.admin_dashboard import admin_dashboard_router

# Student Routes 
from Students.enrollments import enrollments_router
from Students.student import students_router
from Students.student_dashboard import student_dashboard_router
from Students.student_update import update_student_router as update_student_router

# Login (both admin & student) 
from Login.login import router as login_router
from Students.logout import logout_router


app = FastAPI(title="STEI Workshop Management")

# Admin 
app.include_router(categories_router)
app.include_router(workshops_router)
app.include_router(batches_router)
app.include_router(students_router_admin)
app.include_router(quotes_router)
app.include_router(admin_dashboard_router)

# Student 
app.include_router(enrollments_router)
app.include_router(students_router)
app.include_router(student_dashboard_router)
app.include_router(update_student_router)

# Shared 
app.include_router(login_router)
app.include_router(logout_router)
