"""Test configuration and fixtures."""
import asyncio
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.database import Base, get_db, override_engine
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.models import Organization, User


# Use SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create and teardown tables for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db():
    """Provide a test database session."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def org(db: AsyncSession):
    """Create a test organization."""
    org = Organization(
        id=uuid.uuid4(),
        name="Test Org",
        slug="test-org",
        enabled_countries=["NG", "US"],
        is_demo=True,
    )
    db.add(org)
    await db.commit()
    return org


@pytest_asyncio.fixture
async def user(db: AsyncSession, org):
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        organization_id=org.id,
        email="test@test.com",
        hashed_password=hash_password("testpass123"),
        full_name="Test User",
        role="admin",
    )
    db.add(user)
    await db.commit()
    return user


@pytest_asyncio.fixture
async def auth_headers(user: User):
    """Provide authorization headers for authenticated requests."""
    token = create_access_token(user.id, user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def client(db: AsyncSession):
    """Provide an async test client."""

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
