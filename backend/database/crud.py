"""CRUD operations for database models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from backend.database.models import (
    APIKey,
    AuditLog,
    Dataset,
    Prediction,
    Tenant,
    TrainingRun,
)


class TenantCRUD:
    """Tenant CRUD operations."""

    @staticmethod
    def create(db: Session, tenant_id: str, name: str) -> Tenant:
        tenant = Tenant(tenant_id=tenant_id, name=name)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        return tenant

    @staticmethod
    def get(db: Session, tenant_id: str) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()

    @staticmethod
    def get_or_create(db: Session, tenant_id: str, name: str) -> Tenant:
        tenant = TenantCRUD.get(db, tenant_id)
        if tenant is None:
            tenant = TenantCRUD.create(db, tenant_id, name)
        return tenant


class DatasetCRUD:
    """Dataset CRUD operations."""

    @staticmethod
    def create(
        db: Session,
        dataset_id: str,
        tenant_id: str,
        name: str,
        description: str = "",
        row_count: int = 0,
        columns: list[str] | None = None,
        file_key: str = "",
        file_size_bytes: int = 0,
    ) -> Dataset:
        dataset = Dataset(
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            row_count=row_count,
            columns=columns or [],
            file_key=file_key,
            file_size_bytes=file_size_bytes,
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    @staticmethod
    def get(db: Session, dataset_id: str, tenant_id: str) -> Dataset | None:
        return (
            db.query(Dataset)
            .filter(Dataset.dataset_id == dataset_id, Dataset.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def list_by_tenant(db: Session, tenant_id: str) -> list[Dataset]:
        return db.query(Dataset).filter(Dataset.tenant_id == tenant_id).order_by(Dataset.created_at.desc()).all()

    @staticmethod
    def delete(db: Session, dataset_id: str, tenant_id: str) -> None:
        dataset = DatasetCRUD.get(db, dataset_id, tenant_id)
        if dataset:
            db.delete(dataset)
            db.commit()


class TrainingRunCRUD:
    """TrainingRun CRUD operations."""

    @staticmethod
    def create(
        db: Session,
        run_id: str,
        tenant_id: str,
        dataset_id: str,
        config: dict[str, Any] | None = None,
    ) -> TrainingRun:
        run = TrainingRun(
            run_id=run_id,
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            config=config or {},
            status="pending",
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def get(db: Session, run_id: str, tenant_id: str) -> TrainingRun | None:
        return (
            db.query(TrainingRun)
            .filter(TrainingRun.run_id == run_id, TrainingRun.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def update_status(
        db: Session,
        run_id: str,
        status: str,
        metrics: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> TrainingRun | None:
        run = db.query(TrainingRun).filter(TrainingRun.run_id == run_id).first()
        if run:
            run.status = status
            if status == "running" and run.started_at is None:
                run.started_at = datetime.utcnow()
            if status == "completed":
                run.completed_at = datetime.utcnow()
            if metrics:
                run.metrics = metrics
            if error_message:
                run.error_message = error_message
            db.commit()
            db.refresh(run)
        return run

    @staticmethod
    def list_by_tenant(db: Session, tenant_id: str) -> list[TrainingRun]:
        return (
            db.query(TrainingRun)
            .filter(TrainingRun.tenant_id == tenant_id)
            .order_by(TrainingRun.created_at.desc())
            .all()
        )


class PredictionCRUD:
    """Prediction CRUD operations."""

    @staticmethod
    def create(
        db: Session,
        prediction_id: str,
        run_id: str,
        input_data: dict[str, Any] | None = None,
        prediction_value: float | None = None,
        lower_bound: float | None = None,
        upper_bound: float | None = None,
        confidence: float | None = None,
    ) -> Prediction:
        prediction = Prediction(
            prediction_id=prediction_id,
            run_id=run_id,
            input_data=input_data or {},
            prediction_value=prediction_value,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            confidence=confidence,
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction

    @staticmethod
    def list_by_run(db: Session, run_id: str) -> list[Prediction]:
        return db.query(Prediction).filter(Prediction.run_id == run_id).order_by(Prediction.created_at.desc()).all()


class AuditLogCRUD:
    """AuditLog CRUD operations."""

    @staticmethod
    def log(
        db: Session,
        log_id: str,
        tenant_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        log = AuditLog(
            log_id=log_id,
            tenant_id=tenant_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def list_by_tenant(db: Session, tenant_id: str, limit: int = 100) -> list[AuditLog]:
        return (
            db.query(AuditLog)
            .filter(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
