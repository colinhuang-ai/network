#!/usr/bin/env python3
"""
Script tự động hóa cấu hình cổng Switch khi có nhân viên mới vào làm.
- Cấu hình interface (port) dành cho nhân viên mới
- Thiết lập VLAN tương ứng (Admin / Guest / Staff)
- Đặt Description rõ ràng để dễ quản lý
- Kích hoạt port (no shutdown) và lưu cấu hình
"""

import sys
import argparse
from typing import List, Optional
from config import SWITCH_DEVICE, VLANS

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



def format_port_name(port: str) -> str:
    """Chuẩn hóa tên cổng mạng (VD: fa0/18 -> FastEthernet0/18 hoặc giữ nguyên)."""
    p = port.strip()
    if p.lower().startswith("fa0/"):
        return f"FastEthernet0/{p.split('/')[-1]}"
    elif p.lower().startswith("gi0/"):
        return f"GigabitEthernet0/{p.split('/')[-1]}"
    return p


def generate_onboarding_commands(employee_name: str, vlan_id: int, port: str, dept: Optional[str] = None) -> List[str]:
    """Tạo danh sách các câu lệnh Cisco CLI để cấu hình cổng cho nhân viên mới."""
    vlan_info = VLANS.get(vlan_id, {"name": f"VLAN_{vlan_id}"})
    vlan_name = vlan_info["name"]

    dept_str = f" - Phong: {dept}" if dept else ""
    description = f"Nhan vien: {employee_name}{dept_str} - VLAN {vlan_id} ({vlan_name})"

    commands = [
        f"! Cấu hình cổng mạng cho nhân viên mới: {employee_name}",
        f"interface {port}",
        f" description {description}",
        " switchport mode access",
        f" switchport access vlan {vlan_id}",
        " no shutdown",
        "exit"
    ]
    return commands


def interactive_input() -> tuple:
    """Thu thập thông tin nhân viên mới qua giao diện dòng lệnh tương tác."""
    print(f"\n{CYAN}--- NHẬP THÔNG TIN NHÂN VIÊN MỚI ---{RESET}")
    
    name = input("1. Họ và tên nhân viên    : ").strip()
    while not name:
        print(f"{RED}   [!] Tên không được để trống.{RESET}")
        name = input("   Họ và tên nhân viên    : ").strip()

    dept = input("2. Phòng ban (Tùy chọn)   : ").strip()

    print("\n3. Chọn VLAN dành cho nhân viên:")
    vlan_list = list(VLANS.items())
    for idx, (vid, vinfo) in enumerate(vlan_list, 1):
        print(f"   [{idx}] VLAN {vid} - {vinfo['name']} ({vinfo['description']})")

    vlan_choice = input(f"   Vui lòng chọn [1-{len(vlan_list)}] (Mặc định 3 - Staff): ").strip()
    if not vlan_choice:
        vlan_id = 30
    else:
        try:
            choice_idx = int(vlan_choice) - 1
            if 0 <= choice_idx < len(vlan_list):
                vlan_id = vlan_list[choice_idx][0]
            else:
                vlan_id = int(vlan_choice)
        except ValueError:
            vlan_id = 30

    default_range = VLANS.get(vlan_id, {}).get("default_range", "fa0/16-24")
    port = input(f"4. Cổng kết nối trên Switch (VD: fa0/18, dải gợi ý {default_range}): ").strip()
    while not port:
        print(f"{RED}   [!] Tên cổng không được để trống.{RESET}")
        port = input("   Cổng kết nối trên Switch : ").strip()

    return name, vlan_id, format_port_name(port), dept if dept else None


def onboard_employee(name: str, vlan_id: int, port: str, dept: Optional[str] = None, dry_run: bool = False, device_override: dict = None):
    device = device_override if device_override else SWITCH_DEVICE
    commands = generate_onboarding_commands(name, vlan_id, port, dept)

    print(f"\n{CYAN}==================================================")
    print(f"   ONBOARDING NEW EMPLOYEE - NETWORK PORT CONFIG")
    print(f"=================================================={RESET}")
    print(f"Nhân viên   : {name}")
    print(f"Phòng ban   : {dept if dept else 'N/A'}")
    print(f"VLAN Gán    : {vlan_id} ({VLANS.get(vlan_id, {}).get('name', 'Unknown')})")
    print(f"Port Switch : {port}")
    print(f"Mode        : {'DRY-RUN (GIẢ LẬP)' if dry_run else 'LIVE CONNECT'}\n")

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

        print(f"{YELLOW}[*] Đang gửi câu lệnh cấp cổng cho nhân viên '{name}'...{RESET}")
        output = net_connect.send_config_set(commands)
        print(output)

        print(f"{YELLOW}[*] Đang lưu cấu hình vào NVRAM (write memory)...{RESET}")
        save_output = net_connect.save_config()
        print(save_output)

        net_connect.disconnect()
        print(f"\n{GREEN}[✔] Cấp cổng cho nhân viên mới '{name}' trên port {port} thành công!{RESET}\n")
        return True

    except Exception as e:
        print(f"\n{RED}[❌] Đã xảy ra lỗi khi kết nối hoặc gửi lệnh tới Switch:{RESET}")
        print(f"{RED}    {e}{RESET}\n")
        return False


def main():
    parser = argparse.ArgumentParser(description="Script cấp phát và cấu hình cổng Switch khi có nhân viên mới vào làm.")
    parser.add_argument("--name", type=str, help="Họ và tên nhân viên mới.")
    parser.add_argument("--vlan", type=int, choices=[10, 20, 30], help="ID của VLAN (10: Admin, 20: Guest, 30: Staff).")
    parser.add_argument("--port", type=str, help="Tên cổng trên Switch (VD: fa0/18).")
    parser.add_argument("--dept", type=str, help="Tên phòng ban.")
    parser.add_argument("--dry-run", action="store_true", help="Chạy ở chế độ giả lập, chỉ in lệnh CLI ra màn hình.")
    parser.add_argument("--host", type=str, help="Địa chỉ IP của Switch (ghi đè config).")

    args = parser.parse_args()

    device = SWITCH_DEVICE.copy()
    if args.host:
        device["host"] = args.host

    # Nếu không truyền tên hoặc vlan hoặc port -> Chuyển sang chế độ tương tác (Interactive)
    if not (args.name and args.vlan and args.port):
        name, vlan_id, port, dept = interactive_input()
    else:
        name = args.name
        vlan_id = args.vlan
        port = format_port_name(args.port)
        dept = args.dept

    onboard_employee(name, vlan_id, port, dept, dry_run=args.dry_run, device_override=device)


if __name__ == "__main__":
    main()
