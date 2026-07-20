from fastapi import HTTPException, status

class AuthException(HTTPException):
    """Base authentication exception"""
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=status_code, detail=detail)

class UserAlreadyExistsException(AuthException):
    """User already exists exception"""
    def __init__(self, email: str):
        super().__init__(
            detail=f"User with email {email} already exists",
            status_code=status.HTTP_409_CONFLICT
        )

class InvalidCredentialsException(AuthException):
    """Invalid credentials exception"""
    def __init__(self):
        super().__init__(
            detail="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class AuthenticationException(AuthException):
    """Authentication exception"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class UserNotFoundException(AuthException):
    """User not found exception"""
    def __init__(self, user_id: int):
        super().__init__(
            detail=f"User with ID {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

class ValidationException(HTTPException):
    """Validation exception"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class PermissionDeniedException(HTTPException):
    """Permission denied exception"""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class ResourceNotFoundException(HTTPException):
    """Resource not found exception"""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with {identifier} not found"
        )

class DatabaseException(HTTPException):
    """Database operation exception"""
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )