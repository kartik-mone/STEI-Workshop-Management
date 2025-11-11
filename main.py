from fastapi import FastAPI

# AUTH Admin 

# ADMIN Admin
from Admin.categories import router as categories_router
from Admin.workshops import workshops_router
from Admin.batches import batches_router
from Admin.students import students_router_admin
from Admin.quote import quotes_router
from Admin.admin_dashboard import admin_dashboard_router
from Admin.resources_student import resource_router as admin_resource_router
from Admin.clarity_call import students_router_admin as clarity_call_router_admin

# STUDENT Admin
from Students.enrollments import enrollments_router
from Students.student import students_router
from Students.student_dashboard import student_dashboard_router
from Students.student_update import update_student_router
from Students.clarity_call import clarity_call_router
from Students.resources import resource_router


from auth.Login_Logout.login import router as login_router
from auth.Login_Logout.logout import router as logout_router

from auth.Google_Login.oauth_google import router as google_oauth_router

from auth.OTP.otp_auth import router as otp_auth_router

from auth.Microsoft_Login.oauth_microsoft import router as microsoft_oauth_router

app = FastAPI(title="STEI Workshop Management API")



# ADMIN
app.include_router(categories_router)
app.include_router(workshops_router)
app.include_router(batches_router)
app.include_router(students_router_admin)
app.include_router(quotes_router)
app.include_router(admin_dashboard_router)
app.include_router(admin_resource_router)
app.include_router(clarity_call_router_admin)


# STUDENT
app.include_router(enrollments_router)
app.include_router(students_router)
app.include_router(student_dashboard_router)
app.include_router(update_student_router)
app.include_router(clarity_call_router)
app.include_router(resource_router)

app.include_router(login_router) # /login/student and /login/admin
app.include_router(logout_router) # /logout/student and /logout/admin
app.include_router(google_oauth_router) # /auth/google
app.include_router(otp_auth_router) # /auth/student/send_otp    and    /auth/student/verify_otp
app.include_router(microsoft_oauth_router) # /auth/microsoft/login  and  /auth/microsoft/callback
