"""Constants for API Gateway."""

KEY_ACTIVE = 'active'
KEY_REVOKED = 'revoked'
KEY_EXPIRED = 'expired'

KEY_STATUS_CHOICES = [
    (KEY_ACTIVE, 'Active'),
    (KEY_REVOKED, 'Revoked'),
    (KEY_EXPIRED, 'Expired'),
]

SCOPE_READ = 'read'
SCOPE_WRITE = 'write'
SCOPE_ADMIN = 'admin'
SCOPE_CHOICES = (SCOPE_READ, SCOPE_WRITE, SCOPE_ADMIN)
