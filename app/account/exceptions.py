class AccountError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class UserAlreadyExistsError(AccountError):
    pass


class InvalidCredentialsError(AccountError):
    pass


class UserNotFoundError(AccountError):
    pass


class UserAlreadyActiveError(AccountError):
    pass


class UserIsNotAdminError(AccountError):
    pass


class AccessDenied(AccountError):
    pass


class TokenExpiredError(AuthenticationError):
    pass


class InvalidTokenError(AuthenticationError):
    pass
