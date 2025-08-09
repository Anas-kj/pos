from enum import Enum


class RoleType(Enum):
    ADMIN = "Admin"
    InventoryManager = "InventoryManager"
    Superuser = "Superuser"
    Vendor = "Vendor"