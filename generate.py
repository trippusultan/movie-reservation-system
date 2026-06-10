from pathlib import Path

base = Path(r'C:/Users/Spoidy/movie-reservation-system')
(base / 'app').mkdir(exist_ok=True)
(base / 'tests').mkdir(exist_ok=True)

files = {}

files['C:/Users/Spoidy/movie-reservation-system/requirements.txt'] = """fastapi
uvicorn
sqlalchemy
pydantic
python-jose[cryptography]
passlib[bcrypt]
python-multipart
pytest
pytest-asyncio
httpx
python-dotenv
email-validator
bcrypt==4.1.2
"""

files['C:/Users/Spoidy/movie-reservation-system/README.md'] = """# Movie Reservation System

FastAPI backend for movie reservations.

- Project: https://roadmap.sh/projects/movie-reservation-system
- Repo: https://github.com/trippusultan/movie-reservation-system

## Run
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

## Test
pytest -v
"""

files['C:/Users/Spoidy/movie-reservation-system/conftest.py'] = """import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
"""

files['C:/Users/Spoidy/movie-reservation-system/app/__init__.py'] = ""
files['C:/Users/Spoidy/movie-reservation-system/app/models.py'] = '''from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, default=True)

    reservations = relationship("Reservation", back_populates="user")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    genre = Column(String(100), nullable=False)
    poster_url = Column(String(500), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)

    showtimes = relationship("Showtime", back_populates="movie")


class Showtime(Base):
    __tablename__ = "showtimes"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    total_seats = Column(Integer, nullable=False, default=100)
    price = Column(Numeric(10, 2), nullable=False, default=10.00)

    movie = relationship("Movie", back_populates="showtimes")
    seats = relationship("Seat", back_populates="showtime", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="showtime")


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    showtime_id = Column(Integer, ForeignKey("showtimes.id"), nullable=False)
    seat_number = Column(String(10), nullable=False)
    row_letter = Column(String(2), nullable=False)
    seat_index = Column(Integer, nullable=False)
    is_reserved = Column(Boolean, default=False)

    showtime = relationship("Showtime", back_populates="seats")
    reservations = relationship("Reservation", back_populates="seat")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    showtime_id = Column(Integer, ForeignKey("showtimes.id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id"), nullable=False)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="reservations")
    showtime = relationship("Showtime", back_populates="reservations")
    seat = relationship("Seat", back_populates="reservations")
'''

files['C:/Users/Spoidy/movie-reservation-system/app/database.py'] = '''from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./movies.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

files['C:/Users/Spoidy/movie-reservation-system/app/auth.py'] = '''from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "test-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        return TokenData(username=username, user_id=user_id, role=role)
    except JWTError:
        raise
'''

files['C:/Users/Spoidy/movie-reservation-system/app/schemas.py'] = '''from pydantic import BaseModel, EmailStr
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
'''

files['C:/Users/Spoidy/movie-reservation-system/app/main.py'] = '''from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
from app.database import SessionLocal, engine, Base
from app import models, auth
from app.schemas import (
    UserCreate, UserLogin, TokenWithUser, UserOut,
    MovieCreate, MovieUpdate, MovieOut,
    ShowtimeCreate, ShowtimeUpdate, ShowtimeOut,
    SeatOut, ReservationCreate, ReservationOut, AdminReport,
)
from app.models import User, Movie, Showtime, Seat, Reservation

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Reservation System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    token_data = auth.decode_token(token)
    if not token_data.username or token_data.user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@app.get("/health")
def health():
    return {"status": "ok"}


# Auth
@app.post("/register", response_model=TokenWithUser, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = auth.get_password_hash(user_in.password)
    user = User(username=user_in.username, email=user_in.email, hashed_password=hashed, role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    token = auth.create_access_token({"sub": user.username, "user_id": user.id, "role": user.role})
    return TokenWithUser(access_token=token, user=UserOut.from_orm(user))


@app.post("/login", response_model=TokenWithUser)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": user.username, "user_id": user.id, "role": user.role})
    return TokenWithUser(access_token=token, user=UserOut.from_orm(user))


@app.post("/users/promote", response_model=UserOut)
def promote_user(
    username: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = "admin"
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.from_orm(user)


@app.get("/users/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return UserOut.from_orm(current_user)


# Movies
@app.post("/movies", response_model=MovieOut, status_code=201)
def create_movie(movie_in: MovieCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    movie = Movie(**movie_in.dict())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return MovieOut.from_orm(movie)


@app.get("/movies", response_model=List[MovieOut])
def list_movies(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(Movie).filter(Movie.is_active == True)
    return q.offset(skip).limit(limit).all()


@app.get("/movies/search", response_model=List[MovieOut])
def search_movies(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return db.query(Movie).filter(Movie.title.ilike(f"%{q}%"), Movie.is_active == True).all()


# Showtimes
@app.post("/showtimes", response_model=ShowtimeOut, status_code=201)
def create_showtime(showtime_in: ShowtimeCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    movie = db.query(Movie).filter(Movie.id == showtime_in.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    showtime = Showtime(**showtime_in.dict())
    db.add(showtime)
    db.flush()
    for i in range(1, showtime.total_seats + 1):
        row_letter = chr(64 + ((i - 1) // 10) + 1)
        seat_index = ((i - 1) % 10) + 1
        seat = Seat(showtime_id=showtime.id, seat_number=f"{row_letter}{seat_index}", row_letter=row_letter, seat_index=seat_index)
        db.add(seat)
    db.commit()
    db.refresh(showtime)
    return ShowtimeOut.from_orm(showtime)


@app.get("/movies/{movie_id}/showtimes", response_model=List[ShowtimeOut])
def get_showtimes_for_movie(
    movie_id: int,
    date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Showtime).filter(Showtime.movie_id == movie_id)
    if date:
        try:
            day_start = datetime.strptime(date, "%Y-%m-%d")
            day_end = day_start + timedelta(days=1)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        q = q.filter(Showtime.start_time >= day_start, Showtime.start_time < day_end)
    return q.all()


@app.get("/showtimes/{showtime_id}", response_model=ShowtimeOut)
def get_showtime(showtime_id: int, db: Session = Depends(get_db)):
    showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
    if not showtime:
        raise HTTPException(status_code=404, detail="Showtime not found")
    return ShowtimeOut.from_orm(showtime)


@app.get("/showtimes/{showtime_id}/seats", response_model=List[SeatOut])
def get_seats_for_showtime(showtime_id: int, db: Session = Depends(get_db)):
    showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
    if not showtime:
        raise HTTPException(status_code=404, detail="Showtime not found")
    return db.query(Seat).filter(Seat.showtime_id == showtime_id).order_by(Seat.seat_number).all()


@app.get("/showtimes/available", response_model=List[ShowtimeOut])
def list_available_showtimes(db: Session = Depends(get_db), date: Optional[str] = None):
    q = db.query(Showtime)
    if date:
        try:
            day_start = datetime.strptime(date, "%Y-%m-%d")
            day_end = day_start + timedelta(days=1)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
        q = q.filter(Showtime.start_time >= day_start, Showtime.start_time < day_end)
    return q.all()


# Reservations
@app.post("/reservations", response_model=ReservationOut, status_code=201)
def create_reservation(reservation_in: ReservationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    seat = db.query(Seat).filter(Seat.id == reservation_in.seat_id, Seat.showtime_id == reservation_in.showtime_id).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found for this showtime")
    if seat.is_reserved:
        raise HTTPException(status_code=409, detail="Seat already reserved")
    showtime = db.query(Showtime).filter(Showtime.id == reservation_in.showtime_id).first()
    if not showtime:
        raise HTTPException(status_code=404, detail="Showtime not found")
    if showtime.start_time < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Cannot reserve for past showtime")
    reservation = Reservation(
        user_id=current_user.id,
        showtime_id=showtime.id,
        seat_id=seat.id,
        status="active",
    )
    seat.is_reserved = True
    db.add(seat)
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return ReservationOut(
        id=reservation.id,
        showtime_id=reservation.showtime_id,
        user_id=reservation.user_id,
        seat_id=reservation.seat_id,
        status=reservation.status,
        created_at=reservation.created_at,
        showtime=ShowtimeOut.from_orm(showtime) if showtime else None,
        seat=SeatOut.from_orm(seat) if seat else None,
    )


@app.get("/reservations/me", response_model=List[ReservationOut])
def get_my_reservations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reservations = db.query(Reservation).filter(Reservation.user_id == current_user.id, Reservation.status == "active").all()
    result = []
    for r in reservations:
        result.append(ReservationOut(
            id=r.id,
            showtime_id=r.showtime_id,
            user_id=r.user_id,
            seat_id=r.seat_id,
            status=r.status,
            created_at=r.created_at,
            showtime=ShowtimeOut.from_orm(r.showtime) if r.showtime else None,
            seat=SeatOut.from_orm(r.seat) if r.seat else None,
        ))
    return result


@app.delete("/reservations/{reservation_id}")
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.user_id == current_user.id,
        Reservation.status == "active",
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    showtime = db.query(Showtime).filter(Showtime.id == reservation.showtime_id).first()
    if showtime and showtime.start_time < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Cannot cancel past showtime reservation")
    seat = db.query(Seat).filter(Seat.id == reservation.seat_id).first()
    if seat:
        seat.is_reserved = False
        db.add(seat)
    reservation.status = "cancelled"
    db.add(reservation)
    db.commit()
    return {"message": "Reservation cancelled"}


@app.get("/admin/reservations", response_model=List[ReservationOut])
def admin_get_reservations(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    reservations = db.query(Reservation).all()
    result = []
    for r in reservations:
        result.append(ReservationOut(
            id=r.id,
            showtime_id=r.showtime_id,
            user_id=r.user_id,
            seat_id=r.seat_id,
            status=r.status,
            created_at=r.created_at,
            showtime=ShowtimeOut.from_orm(r.showtime) if r.showtime else None,
            seat=SeatOut.from_orm(r.seat) if r.seat else None,
        ))
    return result


@app.get("/admin/report", response_model=AdminReport)
def admin_report(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    total_reservations = db.query(Reservation).count()
    paid = db.query(Reservation).filter(Reservation.status == "active").all()
    total_seats_reserved = sum(1 for r in paid)
    total_seats = db.query(func.sum(Showtime.total_seats)).scalar() or 0
    total_revenue = sum(float(r.showtime.price) for r in paid if r.showtime)
    return AdminReport(
        total_reservations=total_reservations,
        total_seats_reserved=total_seats_reserved,
        total_seats_available=int(total_seats - total_seats_reserved),
        total_revenue=round(total_revenue, 2),
    )
'''

for path, content in files.items():
    Path(path).write_text(content, encoding="utf-8")

print(f"generated {len(files)} files")