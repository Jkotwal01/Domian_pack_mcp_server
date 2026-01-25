
class DatabaseError(Exception):
    """Raised when database operations fail"""
    pass

class SessionNotFoundError(DatabaseError):
    """Raised when session doesn't exist"""
    pass

class VersionNotFoundError(DatabaseError):
    """Raised when version doesn't exist"""
    pass
