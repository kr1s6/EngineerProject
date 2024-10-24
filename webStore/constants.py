from enum import Enum

POSSIBLE_EMAIL_DOMAIN_TLD = [
    "com",
    "org",
    "net",
    "info",
    "biz",
    "edu",
    "gov",
    "mil",
    "co",
    "me",
    "io",
    "app",
    "tv",
    "pro",
    "name",
    "jobs",
    "xyz",
    "online",
    'pl'
]


class OrderStatus(Enum):
    PENDING = 'pending'
    IN_DELIVERY = 'in_delivery'
    DELIVERED = 'delivered'


class UserGender(Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'  # ??


PHONE_NUMBER_PATTERNS = {
    'dashed': r'^\d{3}-\d{3}-\d{3}$',
    'together': r'^\d{9}$'
}
