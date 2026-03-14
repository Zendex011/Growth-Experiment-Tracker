from uuid import uuid4
from datetime import datetime, timezone
from ..extensions import db


class Experiment(db.Model):
    __tablename__ = "experiments"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    title = db.Column(db.String(200), nullable=False)
    hypothesis = db.Column(db.Text, nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_baseline = db.Column(db.Float, nullable=False)

    # State: draft | running | paused | completed
    state = db.Column(
        db.String(20),
        nullable=False,
        default="draft",
    )

    # Verdict: only set when state = completed
    verdict = db.Column(db.String(20), nullable=True)        # ship | rollback | iterate
    verdict_reason = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    results = db.relationship(
        "ExperimentResult",
        backref="experiment",
        lazy="select",
        cascade="all, delete-orphan",
    )
    audit_logs = db.relationship(
        "AuditLog",
        backref="experiment",
        lazy="select",
        cascade="all, delete-orphan",
        order_by="AuditLog.created_at",
    )

    def to_dict(self, include_results=False, include_audit=False):
        data = {
            "id": self.id,
            "title": self.title,
            "hypothesis": self.hypothesis,
            "metric_name": self.metric_name,
            "metric_baseline": self.metric_baseline,
            "state": self.state,
            "verdict": self.verdict,
            "verdict_reason": self.verdict_reason,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
        if include_results:
            data["results"] = [r.to_dict() for r in self.results]
        if include_audit:
            data["audit_logs"] = [a.to_dict() for a in self.audit_logs]
        return data

    def __repr__(self):
        return f"<Experiment {self.id} state={self.state!r}>"
