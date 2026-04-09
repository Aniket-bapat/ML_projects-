from pydantic import BaseModel

# ================= LEAVE =================
class LeaveCreate(BaseModel):
    employee_name: str
    employee_email: str
    reason: str


class LeaveResponse(BaseModel):
    id: int
    employee_name: str
    employee_email: str
    reason: str
    status: str

    class Config:
        from_attributes = True  # Pydantic v2


# ================= PROFILE =================
class EmployeeProfileCreate(BaseModel):
    age: int
    gender: str
    department: str
    job_role: str
    job_level: int
    monthly_income: int
    years_at_company: int
    overtime: bool
