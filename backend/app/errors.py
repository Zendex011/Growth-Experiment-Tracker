from flask import jsonify


# ── Custom Exceptions ──────────────────────────────────────────────────────────

class AppError(Exception):
    """Base class for all application errors."""
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404


class InvalidTransitionError(AppError):
    status_code = 422


class ResultRequiredError(AppError):
    status_code = 422


class ConflictError(AppError):
    status_code = 409


class ValidationError(AppError):
    status_code = 400


class VerdictAlreadySetError(AppError):
    status_code = 409


# ── Error Handlers ─────────────────────────────────────────────────────────────

def register_error_handlers(app):

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({
            "error": type(error).__name__,
            "message": error.message,
            "status": error.status_code,
        }), error.status_code

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({
            "error": "NotFound",
            "message": "The requested resource does not exist.",
            "status": 404,
        }), 404

    @app.errorhandler(405)
    def handle_405(error):
        return jsonify({
            "error": "MethodNotAllowed",
            "message": "HTTP method not allowed on this endpoint.",
            "status": 405,
        }), 405

    @app.errorhandler(500)
    def handle_500(error):
        return jsonify({
            "error": "InternalServerError",
            "message": "An unexpected error occurred.",
            "status": 500,
        }), 500
