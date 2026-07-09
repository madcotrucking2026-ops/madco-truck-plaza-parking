import enum


class VehicleType(str, enum.Enum):
    truck = "truck"
    trailer = "trailer"
    bobtail = "bobtail"
    flatbed = "flatbed"
    car = "car"
    other = "other"


class PassType(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class PassStatus(str, enum.Enum):
    active = "active"
    expiring_soon = "expiring_soon"
    expired = "expired"
    cancelled = "cancelled"


class PaymentMethod(str, enum.Enum):
    cash = "cash"
    credit_card = "credit_card"
    debit_card = "debit_card"
    check = "check"
    phone = "phone"


class MonthlyCustomerStatus(str, enum.Enum):
    holding_spot = "holding_spot"
    truck_parked = "truck_parked"
    trailer_parked = "trailer_parked"
    away = "away"
    inactive = "inactive"


class ReminderStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    stopped = "stopped"


class EmployeeRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    attendant = "attendant"


class AuditAction(str, enum.Enum):
    created = "created"
    edited = "edited"
    renewed = "renewed"
    cancelled = "cancelled"
    refund_attempt = "refund_attempt"
    reminder_sent = "reminder_sent"
    search_performed = "search_performed"
