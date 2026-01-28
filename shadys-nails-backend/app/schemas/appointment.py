from datetime import date, time
from pydantic import BaseModel
from typing import Optional


class AppointmentBase(BaseModel):
    worker_id: int
    customer_id: int
    service_id: int
    additional_id: Optional[int] = None

    date: date
    start_time: time
    end_time: time
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentResponse(AppointmentBase):
    id: int
    status: str

    class Config:
        from_attributes = True
