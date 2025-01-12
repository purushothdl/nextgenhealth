class UserAlreadyExistsException(Exception):
    """Raised when a user with the same username or email already exists."""
    pass

class UserNotFoundException(Exception):
    """Raised when a user is not found in the database."""
    pass

class InvalidUserDataException(Exception):
    """Raised when invalid data is provided for user operations."""
    pass

class UnauthorizedAccessException(Exception):
    """Raised when a user tries to access a resource they are not authorized for."""
    pass

class InvalidCredentialsException(Exception):
    """Raised when invalid credentials are provided during login."""
    pass

class TokenValidationException(Exception):
    """Raised when a token is invalid or expired."""
    pass

class DatabaseConnectionException(Exception):
    """Raised when there is an issue connecting to the database."""
    pass

class OperationNotAllowedException(Exception):
    """Raised when an operation is not allowed (e.g., deleting an admin user)."""
    pass

class TicketNotFoundException(Exception):
    """Raised when the user tries to access a ticket which is not present"""
    pass

class NotificationException(Exception):
    """Raised when there is an error with notification"""
    pass