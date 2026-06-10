from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any, Dict
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True


class TokenWithUser(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    genre: str
    poster_url: Optional[str] = None
    duration_minutes: Optional[int] = None


class MovieCreate(MovieBase):
    pass


class MovieUpdate(MovieBase):
    title: Optional[str] = None
    genre: Optional[str] = None


class MovieOut(MovieBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class ShowtimeCreate(BaseModel):
    movie_id: int
    start_time: datetime
    end_time: datetime
    total_seats: int = 100
    price: float = 10.00


class ShowtimeUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_seats: Optional[int] = None
    price: Optional[float] = None


class SeatOut(BaseModel):
    id: int
    seat_number: str
    row_letter: str
    seat_index: int
    is_reserved: bool

    class Config:
        from_attributes = True


class ShowtimeOut(BaseModel):
    id: int
    movie_id: int
    start_time: datetime
    end_time: datetime
    total_seats: int
    price: float
    available_seats: Optional[int] = None
    reserved_seat_count: Optional[int] = None

    class Config:
        from_attributes = True


class ReservationCreate(BaseModel):
    showtime_id: int
    seat_id: int


class ReservationOut(BaseModel):
    id: int
    showtime_id: int
    user_id: int
    seat_id: int
    status: str
    created_at: datetime
    showtime: Optional[ShowtimeOut] = None
    seat: Optional[SeatOut] = None

    class Config:
        from_attributes = True


class AdminReport(BaseModel):
    total_reservations: int
    total_seats_reserved: int
    total_seats_available: int
    total_revenue: float
