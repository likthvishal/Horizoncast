"""Logging and APM integration."""

import json
import logging
import time
from datetime import datetime
from typing import Any

from fastapi import Request


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    logging.basicConfig(
        level=getattr(logging, level),
        handlers=[handler],
    )


class APMTracer:
    """Simple APM tracing for monitoring."""

    def __init__(self):
        self.spans = []

    def start_span(self, name: str, **tags) -> None:
        """Start a span."""
        span = {
            "name": name,
            "start_time": time.time(),
            "tags": tags,
        }
        self.spans.append(span)
        return span

    def end_span(self) -> None:
        """End the current span."""
        if self.spans:
            span = self.spans[-1]
            span["end_time"] = time.time()
            span["duration_ms"] = (span["end_time"] - span["start_time"]) * 1000

    def get_metrics(self) -> dict[str, Any]:
        """Get collected metrics."""
        return {
            "total_spans": len(self.spans),
            "spans": [
                {
                    "name": s["name"],
                    "duration_ms": s.get("duration_ms", 0),
                    "tags": s.get("tags", {}),
                }
                for s in self.spans
            ],
        }


tracer = APMTracer()
