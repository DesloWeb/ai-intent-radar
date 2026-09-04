"""Tests for authentication endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@test.com",
            "password": "password123",
            "full_name": "New User",
            "organization_slug": "test-org",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with existing email fails."""
    # First registration
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@test.com",
            "password": "password123",
            "full_name": "User One",
        },
    )
    # Duplicate
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@test.com",
            "password": "password456",
            "full_name": "User Two",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@test.com",
            "password": "password123",
            "full_name": "Login User",
        },
    )
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Test login with wrong password."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrong@test.com",
            "password": "password123",
            "full_name": "Wrong User",
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient):
    """Test getting current user profile."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@test.com",
            "password": "password123",
            "full_name": "Me User",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "me@test.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@test.com"
    assert data["full_name"] == "Me User"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """Test getting profile without auth fails."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
