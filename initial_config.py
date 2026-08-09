#!/usr/bin/env python3
"""
Script tự động hóa toàn bộ cấu hình ban đầu cho Cisco Switch.
- Khởi tạo VLANs (10 - Admin, 20 - Guest, 30 - Staff)
- Cấu hình các dải cổng Access cho từng VLAN
- Cấu hình cổng Trunk nối tới Router
- Lưu cấu hình vào NVRAM
"""

import sys
import argparse
from typing import List
from config import SWITCH_DEVICE, VLANS, TRUNK_INTERFACES

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = RED = YELLOW = CYAN = RESET = ""



def generate_initial_commands() -> List[str]:
    """Tạo danh sách các câu lệnh cấu hình Cisco IOS từ file cấu hình/dictionary."""
    commands = []

    # 1. Cấu hình VLANs
    commands.append("! --- 1. KHOI TAO VLANS ---")
    for vlan_id, info in VLANS.items():
        commands.append(f"vlan {vlan_id}")
        commands.append(f" name {info['name']}")
    commands.append("exit")

    # 2. Cấu hình cổng Access cho từng dải
    commands.append("! --- 2. CAU HINH ACCESS PORTS ---")
    for vlan_id, info in VLANS.items():
        r = info.get("default_range")
        if r:
            commands.append(f"! Cổng kết nối {info['description']} (VLAN {vlan_id})")
            commands.append(f"interface range {r}")
            commands.append(" switchport mode access")
            commands.append(f" switchport access vlan {vlan_id}")
            commands.append(" no shutdown")
            commands.append("exit")

    # 3. Cấu hình cổng Trunk
    commands.append("! --- 3. CAU HINH TRUNK PORT ---")
    for trunk_int in TRUNK_INTERFACES:
        commands.append(f"! Cổng Trunk nối Router ({trunk_int})")
        commands.append(f"interface {trunk_int}")
        commands.append(" switchport mode trunk")
        commands.append(" no shutdown")
        commands.append("exit")

    return commands


def run_initial_config(dry_run: bool = False, device_override: dict = None):
    device = device_override if device_override else SWITCH_DEVICE
    commands = generate_initial_commands()

    print(f"\n{CYAN}==================================================")
    print(f"   CISCO SWITCH INITIAL CONFIGURATION SCRIPT")
    print(f"=================================================={RESET}")
    print(f"Target Switch IP : {device['host']}")
    print(f"Device Type      : {device['device_type']}")
    print(f"Mode             : {'DRY-RUN (GIẢ LẬP)' if dry_run else 'LIVE CONNECT'}\n")

    if dry_run:
        print(f"{YELLOW}[+] [DRY-RUN MODE] Danh sách câu lệnh sẽ được gửi tới Switch:{RESET}\n")
        print("-" * 50)
        for cmd in commands:
            if cmd.startswith("!"):
                print(f"{CYAN}{cmd}{RESET}")
            else:
                print(f"  {cmd}")
        print("-" * 50)
        print(f"\n{GREEN}[✔] Giả lập chạy thành công! Không có thay đổi thật nào được thực hiện.{RESET}\n")
        return True

    # Thực thi thật qua Netmiko SSH
    try:
        from netmiko import ConnectHandler
    except ImportError:
        print(f"{RED}[❌] Lỗi: Thư viện 'netmiko' chưa được cài đặt.{RESET}")
        print(f"{YELLOW}    Hãy cài đặt bằng câu lệnh: pip install netmiko colorama{RESET}")
        print(f"{YELLOW}    Hoặc chạy với tham số --dry-run để chạy kiểm tra cấu hình giả lập.{RESET}")
        return False

    print(f"{YELLOW}[*] Đang kết nối tới Switch {device['host']} qua SSH...{RESET}")
    try:
        net_connect = ConnectHandler(**device)
        print(f"{GREEN}[✔] Kết nối thành công! Đang vào chế độ Enable...{RESET}")
        net_connect.enable()

        print(f"{YELLOW}[*] Đang gửi các lệnh cấu hình ban đầu...{RESET}")
        output = net_connect.send_config_set(commands)
        print(output)

        print(f"{YELLOW}[*] Đang lưu cấu hình vào NVRAM (write memory)...{RESET}")
        save_output = net_connect.save_config()
        print(save_output)

        net_connect.disconnect()
        print(f"\n{GREEN}[✔] Hoàn tất cấu hình ban đầu cho Switch thành công!{RESET}\n")
        return True

    except Exception as e:
        print(f"\n{RED}[❌] Đã xảy ra lỗi khi kết nối hoặc gửi lệnh tới Switch:{RESET}")
        print(f"{RED}    {e}{RESET}\n")
        return False


def main():
    parser = argparse.ArgumentParser(description="Script tự động hóa cấu hình ban đầu cho Cisco Switch.")
    parser.add_argument("--dry-run", action="store_true", help="Chạy ở chế độ giả lập, chỉ in các câu lệnh CLI ra màn hình.")
    parser.add_argument("--host", type=str, help="Địa chỉ IP của Switch (ghi đè config).")
    parser.add_argument("--user", type=str, help="Username SSH.")
    parser.add_argument("--password", type=str, help="Password SSH.")
    parser.add_argument("--secret", type=str, help="Mật khẩu Enable.")

    args = parser.parse_args()

    device = SWITCH_DEVICE.copy()
    if args.host:
        device["host"] = args.host
    if args.user:
        device["username"] = args.user
    if args.password:
        device["password"] = args.password
    if args.secret:
        device["secret"] = args.secret

    run_initial_config(dry_run=args.dry_run, device_override=device)


if __name__ == "__main__":
    main()
