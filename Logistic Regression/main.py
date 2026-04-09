from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
import pandas as pd
import pickle
import os
from io import StringIO
import csv
from fastapi.responses import StreamingResponse
import models, crud, schemas
from database import engine, SessionLocal
from dotenv import load_dotenv

load_dotenv()

# ================= LOAD ML MODEL =================
with open("ml/attrition_model.pkl", "rb") as f:
    attrition_model = pickle.load(f)
# ================= CONFIG =================
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

ADMIN_EMAILS = ["bapataniket007@gmail.com"]

# ================= APP SETUP =================
app = FastAPI(title="HRMS - Leave & Attrition System")

app.add_middleware(
    SessionMiddleware,
    secret_key="hrms-secret-key"
)

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")

# ================= DB =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= OAUTH =================
oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

# ================= HOME =================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": request.session.get("user"),
            "role": request.session.get("role")
        }
    )

# ================= LOGIN =================
@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token["userinfo"]

    request.session["user"] = user["name"]
    request.session["email"] = user["email"]
    request.session["role"] = "admin" if user["email"] in ADMIN_EMAILS else "employee"

    return RedirectResponse("/profile", status_code=303)

# ================= PROFILE =================
@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("email"):
        return RedirectResponse("/login", status_code=303)

    profile = crud.get_profile_by_email(db, request.session["email"])
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "profile": profile}
    )

@app.post("/profile")
def submit_profile(
    request: Request,
    age: int = Form(...),
    gender: str = Form(...),
    department: str = Form(...),
    job_role: str = Form(...),
    job_level: int = Form(...),
    monthly_income: int = Form(...),
    years_at_company: int = Form(...),
    overtime: str = Form(...),
    db: Session = Depends(get_db)
):
    crud.create_or_update_profile(
        db,
        request.session["email"],
        request.session["user"],
        schemas.EmployeeProfileCreate(
            age=age,
            gender=gender,
            department=department,
            job_role=job_role,
            job_level=job_level,
            monthly_income=monthly_income,
            years_at_company=years_at_company,
            overtime=(overtime == "true")
        )
    )
    return RedirectResponse("/", status_code=303)

# ================= ADMIN – LEAVES =================
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    leaves = crud.get_leaves(db)
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "leaves": leaves}
    )

@app.post("/approve/{leave_id}")
def approve_leave(leave_id: int, db: Session = Depends(get_db)):
    crud.approve_leave(db, leave_id)
    return RedirectResponse("/admin", status_code=303)

# ================= ADMIN – ATTRITION =================
@app.get("/admin/attrition", response_class=HTMLResponse)
def attrition_dashboard(request: Request, db: Session = Depends(get_db)):
    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    employees = crud.get_all_profiles(db)
    return templates.TemplateResponse(
        "attrition_admin.html",
        {"request": request, "employees": employees}
    )

@app.post("/admin/predict/{emp_id}")
def predict_attrition(emp_id: int, db: Session = Depends(get_db)):
    profile = crud.get_profile_by_id(db, emp_id)

    if not profile:
        return {"error": "Profile not found"}

    input_df = pd.DataFrame([{
        "Age": profile.age,
        "MonthlyIncome": profile.monthly_income,
        "YearsAtCompany": profile.years_at_company,
        "JobLevel": profile.job_level,
        "Gender": profile.gender,
        "Department": profile.department,
        "OverTime": "Yes" if profile.overtime else "No"
    }])

    probability = attrition_model.predict_proba(input_df)[0][1]

    return {
        "employee": profile.name,
        "email": profile.email,
        "attrition_risk_percent": round(probability * 100, 2)
    }
# ================= LEAVE =================

# ================= APPLY LEAVE PAGE =================
@app.get("/apply-leave", response_class=HTMLResponse)
def apply_leave_page(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "apply_leave.html",
        {
            "request": request,
            "user": request.session["user"]
        }
    )

@app.post("/leave-form")
def submit_leave(
    request: Request,
    reason: str = Form(...),
    db: Session = Depends(get_db)
):
    crud.create_leave(
        db,
        schemas.LeaveCreate(
            employee_name=request.session["user"],
            employee_email=request.session["email"],
            reason=reason
        )
    )
    return RedirectResponse("/", status_code=303)

# ================= EXPORT LEAVES (ADMIN) =================
@app.get("/export-leaves")
def export_leaves(request: Request, db: Session = Depends(get_db)):
    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    leaves = crud.get_leaves(db)

    output = StringIO()
    writer = csv.writer(output)

    # CSV header
    writer.writerow([
        "ID",
        "Employee Name",
        "Employee Email",
        "Reason",
        "Status"
    ])

    for leave in leaves:
        writer.writerow([
            leave.id,
            leave.employee_name,
            leave.employee_email,
            leave.reason,
            leave.status
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=leave_requests.csv"
        }
    )

# ================= LOGOUT =================
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
