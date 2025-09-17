
from fastapi import FastAPI
from routes.categories import router as categories_router
from routes.workshops import workshops_router
from routes.batches import batches_router
from routes.students import students_router
from routes.quote import quotes_router

from Login.login import router as login_router

app = FastAPI(title="STEI Workshop Management")

app.include_router(categories_router)
app.include_router(workshops_router)
app.include_router(batches_router)
app.include_router(students_router)
app.include_router(quotes_router)

app.include_router(login_router)