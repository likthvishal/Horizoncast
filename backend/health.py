"""Health checks and SLA monitoring."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from backend.database.models import TrainingRun


class HealthChecker:
    """Health check system."""

    def __init__(self):
        self.checks = {}

    def register(self, name: str, check_fn: callable) -> None:
        """Register a health check."""
        self.checks[name] = check_fn

    async def check_all(self) -> dict[str, Any]:
        """Run all health checks."""
        results = {}
        for name, check_fn in self.checks.items():
            try:
                result = await check_fn() if __import__("inspect").iscoroutinefunction(check_fn) else check_fn()
                results[name] = {"status": "healthy", "result": result}
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}

        overall_status = "healthy" if all(r["status"] == "healthy" for r in results.values()) else "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results,
        }


class SLAMonitor:
    """SLA monitoring and alerts."""

    def __init__(self, db: Session):
        self.db = db
        self.slas = {
            "training_completion_time": timedelta(hours=2),
            "prediction_response_time": timedelta(milliseconds=500),
            "api_uptime": 0.999,  # 99.9%
        }

    def check_training_sla(self, run_id: str) -> bool:
        """Check if training completed within SLA."""
        run = self.db.query(TrainingRun).filter(TrainingRun.run_id == run_id).first()
        if not run or not run.completed_at:
            return False

        duration = run.completed_at - run.started_at
        return duration < self.slas["training_completion_time"]

    def get_sla_status(self) -> dict[str, Any]:
        """Get current SLA status."""
        recent_runs = (
            self.db.query(TrainingRun)
            .filter(TrainingRun.completed_at > datetime.utcnow() - timedelta(hours=24))
            .all()
        )

        completed = len([r for r in recent_runs if self.check_training_sla(r.run_id)])
        total = len(recent_runs)

        return {
            "training_sla_compliance": (completed / total * 100) if total > 0 else 0,
            "recent_runs": total,
            "sla_targets": dict(self.slas),
        }


health_checker = HealthChecker()
