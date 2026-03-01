from rest_framework.throttling import ScopedRateThrottle


class RegisterThrottle(ScopedRateThrottle):
    scope = "register_scope"


class PasswordResetThrottle(ScopedRateThrottle):
    scope = "password_reset_scope"
