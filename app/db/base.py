from sqlalchemy.ext.declarative import declarative_base

# Base class for all SQLAlchemy models
Base = declarative_base()

# Import all models here to ensure they are registered with SQLAlchemy
# This is important for create_all() to work properly
from app.models.user import User  # noqa: F401, E402
