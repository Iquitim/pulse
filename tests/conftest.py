import os
import pytest
import importlib.util
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import database
from app.database import Base, get_db, TierConfig, User, LLMServer, SystemSetting, AgentConfig
from app.security import hash_password, create_access_token

# Create in-memory SQLite engine for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Patch app.database engine and SessionLocal to use in-memory test database
database.engine = test_engine
database.SessionLocal = TestingSessionLocal

# Dynamically import FastAPI app instance from root app.py file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_py_path = os.path.join(BASE_DIR, "app.py")
spec = importlib.util.spec_from_file_location("app_main_module", app_py_path)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = app_module.app

@pytest.fixture(scope="function")
def db_session():
    """Create fresh database tables for each test function and yield a session."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    
    # Check if tiers exist before seeding
    if db.query(TierConfig).count() == 0:
        free_tier = TierConfig(
            tier_name="free",
            max_themes=3,
            max_accounts=1,
            max_calendar_items=5,
            daily_post_limit=2
        )
        pro_tier = TierConfig(
            tier_name="pro",
            max_themes=15,
            max_accounts=3,
            max_calendar_items=50,
            daily_post_limit=10
        )
        desk_tier = TierConfig(
            tier_name="desk",
            max_themes=100,
            max_accounts=10,
            max_calendar_items=1000,
            daily_post_limit=50
        )
        db.add_all([free_tier, pro_tier, desk_tier])
    
    # Check if users exist before seeding
    user = db.query(User).filter(User.email == "user@pulse.com").first()
    if not user:
        hashed_pwd = hash_password("user123")
        user = User(
            email="user@pulse.com",
            hashed_password=hashed_pwd,
            role="user",
            plan_tier="free",
            is_active=True,
            must_change_password=False
        )
        db.add(user)
    
    admin = db.query(User).filter(User.email == "admin@pulse.com").first()
    if not admin:
        admin_pwd = hash_password("admin123")
        admin = User(
            email="admin@pulse.com",
            hashed_password=admin_pwd,
            role="admin",
            plan_tier="desk",
            is_active=True,
            must_change_password=False
        )
        db.add(admin)

    db.flush()
    
    # Seed Default AgentConfigs if missing
    if not db.query(AgentConfig).filter(AgentConfig.user_id == user.id).first():
        db.add(AgentConfig(user_id=user.id, tone="informativo", persona_description="Criador de conteúdo tech"))
    if not db.query(AgentConfig).filter(AgentConfig.user_id == admin.id).first():
        db.add(AgentConfig(user_id=admin.id, tone="informativo", persona_description="Administrador do sistema"))

    db.commit()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def user_token(db_session):
    return create_access_token({"sub": "user@pulse.com", "role": "user"})

@pytest.fixture
def admin_token(db_session):
    return create_access_token({"sub": "admin@pulse.com", "role": "admin"})

@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
