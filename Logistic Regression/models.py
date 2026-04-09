from database import Base
from sqlalchemy import Column, Integer, String, Boolean

# ================= LEAVE TABLE =================
class Leave(Base):
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String, nullable=False)
    employee_email = Column(String, nullable=False, index=True)
    reason = Column(String, nullable=False)
    status = Column(String, default="Submitted", nullable=False)


# ================= EMPLOYEE PROFILE =================
class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)

    department = Column(String, nullable=False)
    job_role = Column(String, nullable=False)
    job_level = Column(Integer, nullable=False)

    monthly_income = Column(Integer, nullable=False)
    years_at_company = Column(Integer, nullable=False)
    overtime = Column(Boolean, nullable=False)
