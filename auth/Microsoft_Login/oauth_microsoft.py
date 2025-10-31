import os
import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from database.db import get_db_connection
from auth.jwt.jwt_auth import create_access_token
from dotenv import load_dotenv

load_dotenv()

MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID", "common")
MICROSOFT_REDIRECT_URI = os.getenv("MICROSOFT_REDIRECT_URI", "http://localhost:8000/auth/microsoft/callback")

if not MICROSOFT_CLIENT_ID or not MICROSOFT_CLIENT_SECRET:
    raise RuntimeError("MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET must be set in your environment")

router = APIRouter(prefix="/auth", tags=["Microsoft"])


# Step 1: Redirect user to Microsoft consent page
@router.get("/microsoft/login")
def microsoft_login():
    authorize_url = (
        f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize"
        f"?client_id={MICROSOFT_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={MICROSOFT_REDIRECT_URI}"
        f"&response_mode=query"
        f"&scope=openid%20profile%20email%20User.Read"
        f"&prompt=select_account"
    )
    return RedirectResponse(authorize_url)


# Step 2: Callback endpoint that Microsoft redirects to with ?code=...
@router.get("/microsoft/callback")
def microsoft_callback(code: str = Query(None), error: str = Query(None), conn=Depends(get_db_connection)):
    if error:
        raise HTTPException(status_code=400, detail=f"Microsoft OAuth error: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided by Microsoft")

    # Exchange authorization code for tokens
    token_url = f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": MICROSOFT_CLIENT_ID,
        "scope": "openid profile email User.Read",
        "code": code,
        "redirect_uri": MICROSOFT_REDIRECT_URI,
        "grant_type": "authorization_code",
        "client_secret": MICROSOFT_CLIENT_SECRET,
    }

    try:
        token_resp = requests.post(token_url, data=data, timeout=10)
        token_resp.raise_for_status()
        token_json = token_resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Token exchange failed: {str(e)}")

    access_token = token_json.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Failed to obtain access token from Microsoft")

    # Fetch user profile from Microsoft Graph
    try:
        graph_resp = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"}, timeout=10
        )
        graph_resp.raise_for_status()
        profile = graph_resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch user profile: {str(e)}")

    # Extract best email value (mail or userPrincipalName)
    email = profile.get("mail") or profile.get("userPrincipalName")
    first_name = profile.get("givenName") or ""
    last_name = profile.get("surname") or ""
    ms_id = profile.get("id")  # Microsoft unique id

    if not email:
        raise HTTPException(status_code=400, detail="Microsoft profile did not include an email")

    # Upsert into students table (student-only flow)
    with conn.cursor() as cursor:
        # try find existing by email
        cursor.execute("SELECT student_id, first_name, last_name FROM students WHERE email=%s", (email,))
        student = cursor.fetchone()

        if not student:
            # Insert new student. password empty (or random), google_id/ms_id stored
            cursor.execute(
                """INSERT INTO students
                   (first_name, last_name, email, password, designation)
                   VALUES (%s, %s, %s, %s, %s)""",
                (first_name, last_name, email, "", None)
            )
            conn.commit()
            # fetch inserted student
            cursor.execute("SELECT student_id, first_name, last_name FROM students WHERE email=%s", (email,))
            student = cursor.fetchone()
        else:
            # Optionally update name columns if blank or changed
            update_needed = False
            if (not student.get("first_name")) and first_name:
                update_needed = True
            if (not student.get("last_name")) and last_name:
                update_needed = True

            if update_needed:
                cursor.execute(
                    "UPDATE students SET first_name=%s, last_name=%s WHERE student_id=%s",
                    (first_name or student.get("first_name"), last_name or student.get("last_name"), student["student_id"])
                )
                conn.commit()
                cursor.execute("SELECT student_id, first_name, last_name FROM students WHERE student_id=%s", (student["student_id"],))
                student = cursor.fetchone()

    # Create JWT token
    token_payload = {"student_id": student["student_id"], "role": "student"}
    jwt_token = create_access_token(token_payload)

    # Return JSON (since backend-only flow)
    return {
        "message": "Microsoft login successful",
        "student": {
            "student_id": student["student_id"],
            "first_name": student.get("first_name"),
            "last_name": student.get("last_name"),
            "email": email
        },
        "token": jwt_token
    }

