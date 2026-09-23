from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

class AppException(Exception):
    """Base application exception."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "An unexpected error occurred."

    def __init__(self, detail: str = None, status_code: int = None):
        if detail:
            self.detail = detail
        if status_code:
            self.status_code = status_code
        super().__init__(self.detail)

class ResourceNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "The requested resource was not found."

class BusinessRuleError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "A business rule validation failed."

class UnauthorizedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Could not validate credentials."

class ForbiddenError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Permission denied."

class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Resource conflict detected."

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
