from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app import models  # noqa: F401
from app.config import get_settings
from app.database import Base, get_db
from app.main import app


settings = get_settings()

if not settings.test_database_url:
    raise RuntimeError("TEST_DATABASE_URL must be configured before running tests.")

test_database_name = settings.test_database_url.rsplit("/", maxsplit=1)[-1]

if not test_database_name.endswith("_test"):
    raise RuntimeError(
        "Refusing to run database tests because TEST_DATABASE_URL "
        "does not point to a database ending in '_test'."
    )


test_engine = create_engine(
    settings.test_database_url,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clear_test_database() -> Generator[None, None, None]:
    with test_engine.begin() as connection:
        connection.execute(
    text(
        "TRUNCATE TABLE "
        "memory_stone_events, "
        "memory_stone_places, "
        "memory_stone_people, "
        "memory_stones, "
        "events, "
        "places, "
        "people "
        "RESTART IDENTITY CASCADE"
    )
)

    yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        session = TestingSessionLocal()

        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
