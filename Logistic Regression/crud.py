from sqlalchemy.orm import Session
from models import Leave, EmployeeProfile
from schemas import LeaveCreate

# ================= LEAVE =================
def create_leave(db: Session, leave: LeaveCreate):
    db_leave = Leave(
        employee_name=leave.employee_name,
        employee_email=leave.employee_email,
        reason=leave.reason,
        status="Submitted"
    )
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave


def get_leaves(db: Session):
    return db.query(Leave).all()


def approve_leave(db: Session, leave_id: int):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if leave:
        leave.status = "Approved"
        db.commit()
    return leave


# ================= PROFILE =================
def get_profile_by_email(db: Session, email: str):
    return db.query(EmployeeProfile).filter(EmployeeProfile.email == email).first()

def get_profile_by_id(db: Session, emp_id: int):
    return db.query(EmployeeProfile).filter(EmployeeProfile.id == emp_id).first()

def create_or_update_profile(db: Session, email: str, name: str, data):
    profile = get_profile_by_email(db, email)

    if profile:
        profile.age = data.age
        profile.gender = data.gender
        profile.department = data.department
        profile.job_role = data.job_role
        profile.job_level = data.job_level
        profile.monthly_income = data.monthly_income
        profile.years_at_company = data.years_at_company
        profile.overtime = data.overtime
    else:
        profile = EmployeeProfile(
            email=email,
            name=name,
            age=data.age,
            gender=data.gender,
            department=data.department,
            job_role=data.job_role,
            job_level=data.job_level,
            monthly_income=data.monthly_income,
            years_at_company=data.years_at_company,
            overtime=data.overtime
        )
        db.add(profile)

    db.commit()
    return profile


def get_all_profiles(db: Session):
    return db.query(EmployeeProfile).all()
