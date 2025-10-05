export enum Role {
    Admin = "Admin",
    InventoryManager = "InventoryManager",
    Superuser = "Superuser",
    Vendor = "Vendor"
}

export const roles = [
    { value: Role.Admin, view_value: "Admin"},
    { value: Role.InventoryManager, view_value: "Inventory Manager"},
    { value: Role.Superuser, view_value: "Superuser"},
    { value: Role.Vendor, view_value: "Vendor"}
]