import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app, get_db
from app.database import Base
from app import models, auth
from datetime import datetime, timedelta

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_auth_and_movies_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        reg = await client.post("/register", json={"username": "alice", "email": "a@example.com", "password": "secret"})
        assert reg.status_code == 201
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        movies = await client.post("/movies", json={"title": "Inception", "description": "Dreams", "genre": "Sci-Fi"}, headers=headers)
        assert movies.status_code == 403

        admin_reg = await client.post(
            "/register",
            json={"username": "admin", "email": "admin@example.com", "password": "admin"},
        )
        assert admin_reg.status_code == 201
        db = TestingSessionLocal()
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        admin.role = "admin"
        db.add(admin)
        db.commit()
        admin_token = auth.create_access_token({"sub": admin.username, "user_id": admin.id, "role": admin.role})
        db.close()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        movie = await client.post(
            "/movies",
            json={"title": "Inception", "description": "Dreams", "genre": "Sci-Fi", "duration_minutes": 148},
            headers=admin_headers,
        )
        assert movie.status_code == 201


        start = datetime.utcnow() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        showtime = await client.post(
            "/showtimes",
            json={"movie_id": movie.json()["id"], "start_time": start.isoformat() + "Z", "end_time": end.isoformat() + "Z", "total_seats": 10, "price": 12.5},
            headers=admin_headers,
        )
        assert showtime.status_code == 201

        seats = await client.get(f"/showtimes/{showtime.json()['id']}/seats")
        assert seats.status_code == 200
        assert len(seats.json()) == 10

        res = await client.post("/reservations", json={"showtime_id": showtime.json()["id"], "seat_id": seats.json()[0]["id"]}, headers=headers)
        assert res.status_code == 201

        my_res = await client.get("/reservations/me", headers=headers)
        assert my_res.status_code == 200
        assert len(my_res.json()) == 1

        cancel = await client.delete(f"/reservations/{my_res.json()[0]['id']}", headers=headers)
        assert cancel.status_code == 200

        report = await client.get("/admin/report", headers=admin_headers)
        assert report.status_code == 200
        assert report.json()["total_revenue"] == 0.0
