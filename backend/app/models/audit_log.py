from uuid import uuid4
from datetime import datetime, timezone
import json
from ..extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    experiment_id = db.Column(
        db.String(36),
        db.ForeignKey("experiments.id", ondelete="CASCADE"),
        nullable=False,
    )

    event_type = db.Column(db.String(50), nullable=False)

    from_state = db.Column(db.String(20), nullable=True)
    to_state = db.Column(db.String(20), nullable=True)

    extra_data = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def data(self):
        if self.extra_data:
            return self.extra_data
    

    @data.setter
    def data(self, value: dict):
        self.extra_data = json.dumps(value) if value else None

    def to_dict(self):
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "event_type": self.event_type,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<AuditLog {self.event_type} experiment={self.experiment_id}>"