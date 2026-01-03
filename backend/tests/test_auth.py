import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, get_db
from main import app  # Assuming your main FastAPI app is in main.py
from src.models.user import User
import uuid

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Override dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_register_user():
    """Test user registration"""
    test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "SecurePassword123!"
    
    response = client.post(
        "/rag/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "username": f"testuser_{uuid.uuid4().hex[:8]}"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["email"] == test_email
    assert "message" in data

def test_register_duplicate_email():
    """Test registration with duplicate email fails"""
    test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "SecurePassword123!"
    
    # Register first user
    client.post(
        "/rag/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "username": f"testuser_{uuid.uuid4().hex[:8]}"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/rag/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "username": f"testuser_{uuid.uuid4().hex[:8]}_2"
        }
    )
    
    assert response.status_code == 409

def test_login_user():
    """Test user login"""
    test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "SecurePassword123!"
    
    # Register user first
    register_response = client.post(
        "/rag/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "username": f"testuser_{uuid.uuid4().hex[:8]}"
        }
    )
    
    assert register_response.status_code == 200
    
    # Login with registered user
    response = client.post(
        "/rag/auth/login",
        json={
            "email": test_email,
            "password": test_password
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["email"] == test_email

def test_login_invalid_credentials():
    """Test login with invalid credentials fails"""
    test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "SecurePassword123!"
    
    response = client.post(
        "/rag/auth/login",
        json={
            "email": test_email,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401