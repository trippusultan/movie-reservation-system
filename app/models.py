from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Numeric, func
from sqlalchemy.orm import relationship

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
