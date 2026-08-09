import os

# Thông tin cấu hình kết nối tới Cisco Switch
# Bạn có thể thay đổi các giá trị mặc định ở đây hoặc đặt biến môi trường
SWITCH_DEVICE = {
    "device_type": os.getenv("SWITCH_TYPE", "cisco_ios"),
    "host": os.getenv("SWITCH_HOST", "192.168.1.2"),
    "username": os.getenv("SWITCH_USER", "admin"),
    "password": os.getenv("SWITCH_PASS", "cisco123"),
    "secret": os.getenv("SWITCH_SECRET", "cisco123"),  # Mật khẩu Enable
    "port": int(os.getenv("SWITCH_PORT", 22)),
    "timeout": 10,
}

# Danh sách VLAN chuẩn của hệ thống
VLANS = {
    10: {
        "name": "Admin",
        "description": "PC Lễ tân / Quản lý",
        "default_range": "fa0/1-5"
    },
    20: {
        "name": "Guest",
        "description": "WiFi / Thiết bị Khách",
        "default_range": "fa0/6-15"
    },
    30: {
        "name": "Staff",
        "description": "Thiết bị Nhân viên",
        "default_range": "fa0/16-24"
    }
}

# Cấu hình cổng Trunk kết nối với Router / Switch khác
TRUNK_INTERFACES = [
    "g0/1"
]
