"""SQLAlchemy ORM models for HorizonCast."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Tenant(Base):
    """Represents a customer/tenant in multi-tenant system."""

    __tablename__ = "tenants"

    tenant_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    datasets = relationship("Dataset", back_populates="tenant", cascade="all, delete-orphan")
    training_runs = relationship("TrainingRun", back_populates="tenant", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="tenant", cascade="all, delete-orphan")


class APIKey(Base):
    """API keys for tenant authentication."""

    __tablename__ = "api_keys"

    key_id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), nullable=False, index=True)
    key_hash = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="api_keys")


class Dataset(Base):
    """Represents an uploaded dataset."""

    __tablename__ = "datasets"

    dataset_id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    row_count = Column(Integer, default=0)
    columns = Column(JSON, default={})
    file_key = Column(String, nullable=False)
    file_size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="datasets")
    training_runs = relationship("TrainingRun", back_populates="dataset", cascade="all, delete-orphan")


class TrainingRun(Base):
    """Represents a model training run."""

    __tablename__ = "training_runs"

    run_id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), nullable=False, index=True)
    dataset_id = Column(String, ForeignKey("datasets.dataset_id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")  # pending, running, completed, failed
    config = Column(JSON, default={})
    metrics = Column(JSON, default={})
    error_message = Column(Text, nullable=True)
    model_version = Column(String, nullable=True)
    artifact_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="training_runs")
    dataset = relationship("Dataset", back_populates="training_runs")
    predictions = relationship("Prediction", back_populates="training_run", cascade="all, delete-orphan")


class Prediction(Base):
    """Represents a prediction made by a model."""

    __tablename__ = "predictions"

    prediction_id = Column(String, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("training_runs.run_id"), nullable=False, index=True)
    input_data = Column(JSON, default={})
    prediction_value = Column(Float, nullable=True)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    training_run = relationship("TrainingRun", back_populates="predictions")


class AuditLog(Base):
    """Audit log for compliance and debugging."""

    __tablename__ = "audit_logs"

    log_id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), nullable=False, index=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    details = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


def get_engine(database_url: str):
    """Create SQLAlchemy engine."""
    return create_engine(database_url, echo=False, pool_pre_ping=True)


def create_tables(database_url: str) -> None:
    """Create all tables."""
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
