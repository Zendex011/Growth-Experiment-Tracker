"""
Test configuration and fixtures.

Key decisions:
  - SQLite in-memory for speed and isolation
  - Each test gets a fresh DB via function-scoped fixtures
  - HuggingFace API is always mocked — no real network calls in tests
  - mock_hf_api fixture returns valid JSON by default; tests override as needed
"""

import pytest
from unittest.mock import patch, MagicMock

from app import create_app
from app.extensions import db as _db
from app.models import Experiment, ExperimentResult, AuditLog


# ── App & DB Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    return _db


# ── Model Factories ────────────────────────────────────────────────────────────

@pytest.fixture
def draft_experiment(db):
    """A fresh draft experiment saved to the test DB."""
    exp = Experiment(
        title="Button Colour Test",
        hypothesis="We believe that changing button to green will increase signups by 15% because green signals action.",
        metric_name="signup_rate",
        metric_baseline=3.2,
        state="draft",
    )
    db.session.add(exp)
    db.session.commit()
    return exp


@pytest.fixture
def running_experiment(db, draft_experiment):
    """A draft experiment transitioned to running."""
    from app.services.state_machine import transition
    transition(draft_experiment, "running", db.session)
    db.session.commit()
    return draft_experiment


@pytest.fixture
def experiment_with_result(db, running_experiment):
    """A running experiment that has one result logged."""
    result = ExperimentResult(
        experiment_id=running_experiment.id,
        control_value=3.2,
        variant_value=4.1,
        sample_size_control=1400,
        sample_size_variant=1380,
        duration_days=14,
    )
    db.session.add(result)
    db.session.commit()
    return running_experiment


@pytest.fixture
def completed_experiment(db, experiment_with_result):
    """A running experiment with results transitioned to completed."""
    from app.services.state_machine import transition
    transition(experiment_with_result, "completed", db.session)
    db.session.commit()
    return experiment_with_result


# ── AI Mock Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def mock_hf_hypothesis():
    """
    Mocks HuggingFace API to return a valid hypothesis JSON.
    Use this in any test that calls the /ai/hypothesis endpoint.
    """
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = [
        {
            "generated_text": (
                '{"hypothesis": "We believe that changing the button colour '
                'to green will increase signup rate by 15% because green '
                'signals positive action.", "confidence": "high"}'
            )
        }
    ]
    with patch("app.services.ai_service.requests.post", return_value=fake_response) as mock:
        yield mock


@pytest.fixture
def mock_hf_verdict():
    """Mocks HuggingFace API to return a valid verdict JSON."""
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = [
        {
            "generated_text": (
                '{"verdict": "ship", '
                '"interpretation": "Variant outperformed control by 28%.", '
                '"suggested_reason": "Consistent positive signal over 14 days."}'
            )
        }
    ]
    with patch("app.services.ai_service.requests.post", return_value=fake_response) as mock:
        yield mock


@pytest.fixture
def mock_hf_summary():
    """Mocks HuggingFace API to return a valid summary JSON."""
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = [
        {
            "generated_text": (
                '{"summary": "In a 14-day test, the green button variant '
                'improved signup rate from 3.2% to 4.1%, a 28% relative lift. '
                "The experiment was shipped on March 10. "
                "Next suggested test: button copy variations.\"}"
            )
        }
    ]
    with patch("app.services.ai_service.requests.post", return_value=fake_response) as mock:
        yield mock


@pytest.fixture
def mock_hf_timeout():
    """Mocks HuggingFace API to simulate a timeout."""
    import requests as req
    with patch(
        "app.services.ai_service.requests.post",
        side_effect=req.exceptions.Timeout("Connection timed out"),
    ) as mock:
        yield mock


@pytest.fixture
def mock_hf_503():
    """Mocks HuggingFace API to simulate a model-loading 503."""
    fake_response = MagicMock()
    fake_response.status_code = 503
    fake_response.json.return_value = {"error": "Model is currently loading"}
    with patch("app.services.ai_service.requests.post", return_value=fake_response) as mock:
        yield mock


@pytest.fixture
def mock_hf_bad_json():
    """Mocks HuggingFace API to return text with no valid JSON."""
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = [
        {"generated_text": "Sure! Here is a great hypothesis for you. Just kidding, no JSON here."}
    ]
    with patch("app.services.ai_service.requests.post", return_value=fake_response) as mock:
        yield mock
