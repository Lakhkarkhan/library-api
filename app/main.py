from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from app import config, models  # noqa: F401  (models must be imported to register tables)
from app.database import Base, SessionLocal, engine
from app.routers import auth, books, users
from app.security import hash_password


def seed_admin() -> None:
    """Create an admin user from env vars if one is configured and missing."""
    if not (config.ADMIN_USERNAME and config.ADMIN_PASSWORD):
        return
    with SessionLocal() as db:
        exists = db.scalar(select(models.User).where(models.User.username == config.ADMIN_USERNAME))
        if exists is None:
            db.add(
                models.User(
                    username=config.ADMIN_USERNAME,
                    hashed_password=hash_password(config.ADMIN_PASSWORD),
                    role="admin",
                )
            )
            db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_admin()
    yield


app = FastAPI(
    title="Library API",
    description="A REST API with JWT authentication, role-based access control, and full CRUD.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
