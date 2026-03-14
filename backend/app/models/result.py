from uuid import uuid4
from datetime import datetime, timezone
from ..extensions import db


class ExperimentResult(db.Model):
    __tablename__ = "experiment_results"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    experiment_id = db.Column(
        db.String(36),
        db.ForeignKey("experiments.id", ondelete="CASCADE"),
        nullable=False,
    )

    control_value = db.Column(db.Float, nullable=False)
    variant_value = db.Column(db.Float, nullable=False)
    sample_size_control = db.Column(db.Integer, nullable=False)
    sample_size_variant = db.Column(db.Integer, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)

    recorded_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "control_value": self.control_value,
            "variant_value": self.variant_value,
            "sample_size_control": self.sample_size_control,
            "sample_size_variant": self.sample_size_variant,
            "duration_days": self.duration_days,
            "recorded_at": self.recorded_at.isoformat(),
        }

    def __repr__(self):
        return f"<ExperimentResult {self.id} experiment={self.experiment_id}>"
