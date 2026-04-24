"""Webhook management for event notifications."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

import requests


class EventType(str, Enum):
    """Webhook event types."""

    TRAINING_STARTED = "training.started"
    TRAINING_COMPLETED = "training.completed"
    TRAINING_FAILED = "training.failed"
    PREDICTION_MADE = "prediction.made"
    ANOMALY_DETECTED = "anomaly.detected"


@dataclass
class WebhookEvent:
    """Webhook event payload."""

    event_type: EventType
    run_id: str
    timestamp: str
    data: dict


class WebhookManager:
    """Manage webhook subscriptions and delivery."""

    def __init__(self):
        self.subscriptions: dict[str, list[str]] = {}

    def subscribe(self, event_type: EventType, webhook_url: str) -> None:
        """Subscribe to an event."""
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []
        self.subscriptions[event_type].append(webhook_url)

    def unsubscribe(self, event_type: EventType, webhook_url: str) -> None:
        """Unsubscribe from an event."""
        if event_type in self.subscriptions:
            self.subscriptions[event_type].remove(webhook_url)

    async def emit(self, event: WebhookEvent) -> None:
        """Emit an event to all subscribers."""
        urls = self.subscriptions.get(event.event_type, [])

        for url in urls:
            try:
                requests.post(
                    url,
                    json={
                        "event": event.event_type.value,
                        "run_id": event.run_id,
                        "timestamp": event.timestamp,
                        "data": event.data,
                    },
                    timeout=5,
                )
            except Exception as e:
                # TODO: Log webhook failure
                pass


webhook_manager = WebhookManager()
