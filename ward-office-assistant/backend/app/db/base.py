"""
SQLAlchemy declarative base. Import this `Base` in every model so that
Alembic's autogenerate can discover all tables.

TODO: once models exist, create a base.py import aggregator like:
    from app.models.user import User
    from app.models.service import Service
    from app.models.office import OfficeInfo
so Alembic env.py can `from app.db.base import Base` and see everything.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
