#!/usr/bin/env python3
"""
Ứng dụng Giao Diện Desktop (GUI) Quản Lý & Tự Động Hóa Cisco Switch.
Sử dụng Tkinter & TTK (luồng ngầm Multi-threading cho kết nối SSH).
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Dict

# UTF-8 stdout fix for Windows console compatibility
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import SWITCH_DEVICE, VLANS, TRUNK_INTERFACES
from initial_config import generate_initial_commands
from add_employee import generate_onboarding_commands, format_port_name


class CiscoAutomationGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Cisco Switch Automation Tool - Manager")
        self.root.geometry("850 OPEN 650".replace(" OPEN ", "x"))
        self.root.minsize(780, 550)

        # Style & Theme
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self._configure_styles()
        self._create_layout()

    def _configure_styles(self):
        """Định hình màu sắc và style cho ứng dụng Desktop UI."""
        self.style.configure("TNotebook", background="#f0f2f5", borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[15, 8], background="#e4e6eb")
        self.style.map("TNotebook.Tab", background=[("selected", "#0066cc")], foreground=[("selected", "#ffffff")])

        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#003366")
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 10, "italic"), foreground="#555555")
        self.style.configure("Title.TLabelframe", font=("Segoe UI", 10, "bold"), foreground="#003366")
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=6)
        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background="#0066cc", foreground="#ffffff")
        self.style.configure("Secondary.TButton", font=("Segoe UI", 10, "bold"), background="#28a745", foreground="#ffffff")

    def _create_layout(self):
        """Khởi tạo bố cục màn hình với các Tab."""
        # Top Title Banner
        banner_frame = ttk.Frame(self.root, padding=(15, 10))
        banner_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(banner_frame, text="⚡ CISCO SWITCH AUTOMATION SYSTEM", style="Header.TLabel")
        title_lbl.pack(anchor=tk.W)
        sub_lbl = ttk.Label(banner_frame, text="Hệ thống tự động hóa cấu hình ban đầu & Cấp phát cổng nhân viên mới", style="SubHeader.TLabel")
        sub_lbl.pack(anchor=tk.W)

        # Main Tab Control
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Tab 1: Cấu hình ban đầu
        self.tab_initial = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_initial, text=" ⚙️ 1. Cấu Hình Ban Đầu ")

        # Tab 2: Nhân viên mới
        self.tab_employee = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_employee, text=" 👤 2. Cấp Cổng Nhân Viên Mới ")

        # Tab 3: Thông tin hệ thống
        self.tab_info = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_info, text=" 📊 3. Thông Tin VLAN ")

        self._build_tab_initial()
        self._build_tab_employee()
        self._build_tab_info()

    # =========================================================================
    # TAB 1: CẤU HÌNH BAN ĐẦU
    # =========================================================================
    def _build_tab_initial(self):
        # Frame Cấu hình kết nối Switch
        conn_frame = ttk.LabelFrame(self.tab_initial, text="Thông Tin Kết Nối Switch", style="Title.TLabelframe", padding=10)
        conn_frame.pack(fill=tk.X, pady=(0, 10))

        grid_opts = {'padx': 5, 'pady': 5, 'sticky': tk.W}

        ttk.Label(conn_frame, text="IP Switch:").grid(row=0, column=0, **grid_opts)
        self.init_host_var = tk.StringVar(value=SWITCH_DEVICE["host"])
        ttk.Entry(conn_frame, textvariable=self.init_host_var, width=16).grid(row=0, column=1, **grid_opts)

        ttk.Label(conn_frame, text="Username:").grid(row=0, column=2, **grid_opts)
        self.init_user_var = tk.StringVar(value=SWITCH_DEVICE["username"])
        ttk.Entry(conn_frame, textvariable=self.init_user_var, width=14).grid(row=0, column=3, **grid_opts)

        ttk.Label(conn_frame, text="Password:").grid(row=0, column=4, **grid_opts)
        self.init_pass_var = tk.StringVar(value=SWITCH_DEVICE["password"])
        ttk.Entry(conn_frame, textvariable=self.init_pass_var, show="*", width=14).grid(row=0, column=5, **grid_opts)

        ttk.Label(conn_frame, text="Enable Secret:").grid(row=1, column=0, **grid_opts)
        self.init_secret_var = tk.StringVar(value=SWITCH_DEVICE["secret"])
        ttk.Entry(conn_frame, textvariable=self.init_secret_var, show="*", width=16).grid(row=1, column=1, **grid_opts)

        # Nút điều khiển
        btn_frame = ttk.Frame(self.tab_initial)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        btn_dry_run = ttk.Button(btn_frame, text="🔍 Xem Trước Lệnh (Dry-Run)", command=self._on_initial_dry_run)
        btn_dry_run.pack(side=tk.LEFT, padx=(0, 10))

        btn_exec = ttk.Button(btn_frame, text="⚡ Thực Thi Cấu Hình Ban Đầu", command=self._on_initial_execute)
        btn_exec.pack(side=tk.LEFT)

        # Output Log Box
        log_frame = ttk.LabelFrame(self.tab_initial, text="Nhật Ký Thực Thi / Lệnh CLI Sinh Ra", style="Title.TLabelframe", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.init_log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.init_log_text.pack(fill=tk.BOTH, expand=True)

    def _on_initial_dry_run(self):
        self.init_log_text.delete("1.0", tk.END)
        self._write_log(self.init_log_text, "==================================================\n", "#007acc")
        self._write_log(self.init_log_text, "   CISCO SWITCH INITIAL CONFIG - DRY RUN MODE\n", "#007acc")
        self._write_log(self.init_log_text, "==================================================\n\n", "#007acc")

        commands = generate_initial_commands()
        self._write_log(self.init_log_text, "[+] Danh sách lệnh CLI sẽ được gửi tới Switch:\n\n", "#dcdcaa")
        for cmd in commands:
            if cmd.startswith("!"):
                self._write_log(self.init_log_text, f"{cmd}\n", "#57a64a")
            else:
                self._write_log(self.init_log_text, f"  {cmd}\n", "#d4d4d4")

        self._write_log(self.init_log_text, "\n[✔] Giả lập hoàn tất! Không có thay đổi thật nào trên thiết bị.\n", "#4ec9b0")

    def _on_initial_execute(self):
        device = {
            "device_type": SWITCH_DEVICE["device_type"],
            "host": self.init_host_var.get().strip(),
            "username": self.init_user_var.get().strip(),
            "password": self.init_pass_var.get().strip(),
            "secret": self.init_secret_var.get().strip(),
            "port": SWITCH_DEVICE["port"],
            "timeout": 10,
        }

        if not device["host"]:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập IP Switch!")
            return

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn kết nối tới {device['host']} và thực thi toàn bộ cấu hình ban đầu?"):
            return

        self.init_log_text.delete("1.0", tk.END)
        self._write_log(self.init_log_text, f"[*] Đang khởi chạy luồng kết nối tới {device['host']}...\n", "#ce9178")

        # Start thread
        commands = generate_initial_commands()
        threading.Thread(target=self._ssh_worker, args=(device, commands, self.init_log_text), daemon=True).start()

    # =========================================================================
    # TAB 2: NHÂN VIÊN MỚI
    # =========================================================================
    def _build_tab_employee(self):
        # Form nhập thông tin nhân viên
        emp_frame = ttk.LabelFrame(self.tab_employee, text="Thông Tin Nhân Viên & Cổng Switch", style="Title.TLabelframe", padding=10)
        emp_frame.pack(fill=tk.X, pady=(0, 10))

        grid_opts = {'padx': 8, 'pady': 6, 'sticky': tk.W}

        ttk.Label(emp_frame, text="Họ & Tên Nhân Viên:").grid(row=0, column=0, **grid_opts)
        self.emp_name_var = tk.StringVar(value="Nguyen Van A")
        ttk.Entry(emp_frame, textvariable=self.emp_name_var, width=28).grid(row=0, column=1, **grid_opts)

        ttk.Label(emp_frame, text="Phòng Ban:").grid(row=0, column=2, **grid_opts)
        self.emp_dept_var = tk.StringVar(value="Marketing")
        ttk.Entry(emp_frame, textvariable=self.emp_dept_var, width=24).grid(row=0, column=3, **grid_opts)

        ttk.Label(emp_frame, text="Chọn VLAN:").grid(row=1, column=0, **grid_opts)
        vlan_options = [f"VLAN {vid} - {vinfo['name']} ({vinfo['description']})" for vid, vinfo in VLANS.items()]
        self.emp_vlan_cb = ttk.Combobox(emp_frame, values=vlan_options, state="readonly", width=32)
        self.emp_vlan_cb.current(2)  # Default: VLAN 30 - Staff
        self.emp_vlan_cb.grid(row=1, column=1, **grid_opts)

        ttk.Label(emp_frame, text="Cổng Switch (Port):").grid(row=1, column=2, **grid_opts)
        self.emp_port_var = tk.StringVar(value="fa0/18")
        ttk.Entry(emp_frame, textvariable=self.emp_port_var, width=24).grid(row=1, column=3, **grid_opts)

        # Dry run checkbox
        self.emp_dry_run_var = tk.BooleanVar(value=True)
        chk_dry = ttk.Checkbutton(emp_frame, text="Chạy ở chế độ Giả lập (Dry-Run)", variable=self.emp_dry_run_var)
        chk_dry.grid(row=2, column=0, columnspan=2, **grid_opts)

        # Nút điều khiển
        btn_frame = ttk.Frame(self.tab_employee)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        btn_preview = ttk.Button(btn_frame, text="🔍 Xem Trước Lệnh CLI", command=self._on_employee_preview)
        btn_preview.pack(side=tk.LEFT, padx=(0, 10))

        btn_exec = ttk.Button(btn_frame, text="⚡ Thực Thi Cấp Cổng", command=self._on_employee_execute)
        btn_exec.pack(side=tk.LEFT)

        # Output Log Box
        log_frame = ttk.LabelFrame(self.tab_employee, text="Chi Tiết Lệnh Sinh Ra & Log Kết Nối", style="Title.TLabelframe", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.emp_log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.emp_log_text.pack(fill=tk.BOTH, expand=True)

    def _get_selected_vlan_id(self) -> int:
        selected_str = self.emp_vlan_cb.get()
        try:
            # Parse 'VLAN 30 - Staff...' -> 30
            vlan_id = int(selected_str.split("-")[0].replace("VLAN", "").strip())
            return vlan_id
        except Exception:
            return 30

    def _on_employee_preview(self):
        name = self.emp_name_var.get().strip()
        dept = self.emp_dept_var.get().strip()
        vlan_id = self._get_selected_vlan_id()
        raw_port = self.emp_port_var.get().strip()

        if not name or not raw_port:
            messagebox.showwarning("Cảnh báo", "Tên nhân viên và cổng Switch không được để trống!")
            return

        port = format_port_name(raw_port)
        commands = generate_onboarding_commands(name, vlan_id, port, dept)

        self.emp_log_text.delete("1.0", tk.END)
        self._write_log(self.emp_log_text, "==================================================\n", "#007acc")
        self._write_log(self.emp_log_text, f"   ONBOARDING NEW EMPLOYEE: {name.upper()}\n", "#007acc")
        self._write_log(self.emp_log_text, "==================================================\n", "#007acc")
        self._write_log(self.emp_log_text, f"Phòng ban   : {dept}\n", "#dcdcaa")
        self._write_log(self.emp_log_text, f"VLAN Gán    : {vlan_id}\n", "#dcdcaa")
        self._write_log(self.emp_log_text, f"Port Switch : {port}\n\n", "#dcdcaa")

        self._write_log(self.emp_log_text, "[+] Lệnh Cisco CLI sinh ra:\n\n", "#ce9178")
        for cmd in commands:
            if cmd.startswith("!"):
                self._write_log(self.emp_log_text, f"{cmd}\n", "#57a64a")
            else:
                self._write_log(self.emp_log_text, f"  {cmd}\n", "#d4d4d4")

        self._write_log(self.emp_log_text, "\n[✔] Đã xem trước câu lệnh thành công.\n", "#4ec9b0")

    def _on_employee_execute(self):
        name = self.emp_name_var.get().strip()
        dept = self.emp_dept_var.get().strip()
        vlan_id = self._get_selected_vlan_id()
        raw_port = self.emp_port_var.get().strip()
        is_dry_run = self.emp_dry_run_var.get()

        if not name or not raw_port:
            messagebox.showwarning("Cảnh báo", "Tên nhân viên và cổng Switch không được để trống!")
            return

        port = format_port_name(raw_port)
        commands = generate_onboarding_commands(name, vlan_id, port, dept)

        if is_dry_run:
            self._on_employee_preview()
            return

        device = {
            "device_type": SWITCH_DEVICE["device_type"],
            "host": self.init_host_var.get().strip(),
            "username": self.init_user_var.get().strip(),
            "password": self.init_pass_var.get().strip(),
            "secret": self.init_secret_var.get().strip(),
            "port": SWITCH_DEVICE["port"],
            "timeout": 10,
        }

        if not messagebox.askyesno("Xác nhận", f"Cấp cổng {port} cho nhân viên '{name}' trên Switch {device['host']}?"):
            return

        self.emp_log_text.delete("1.0", tk.END)
        self._write_log(self.emp_log_text, f"[*] Đang thực thi gửi lệnh cấu hình cổng {port} tới Switch...\n", "#ce9178")

        threading.Thread(target=self._ssh_worker, args=(device, commands, self.emp_log_text), daemon=True).start()

    # =========================================================================
    # TAB 3: THÔNG TIN HỆ THỐNG
    # =========================================================================
    def _build_tab_info(self):
        info_frame = ttk.LabelFrame(self.tab_info, text="Danh Sách VLAN Mặc Định Của Hệ Thống", style="Title.TLabelframe", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("VLAN ID", "Tên VLAN", "Mô Tả / Bộ Phận", "Dải Cổng Access Mặc Định")
        tree = ttk.Treeview(info_frame, columns=cols, show="headings", height=8)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=180, anchor=tk.CENTER)

        for vid, vinfo in VLANS.items():
            tree.insert("", tk.END, values=(vid, vinfo["name"], vinfo["description"], vinfo["default_range"]))

        tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        trunk_lbl = ttk.Label(info_frame, text=f"📌 Danh sách cổng Trunk nối Router: {', '.join(TRUNK_INTERFACES)}", font=("Segoe UI", 10, "bold"))
        trunk_lbl.pack(anchor=tk.W)

    # =========================================================================
    # HELPER WORKERS & UTILS
    # =========================================================================
    def _write_log(self, text_widget: scrolledtext.ScrolledText, msg: str, color_hex: str = "#d4d4d4"):
        tag_name = f"color_{color_hex.replace('#', '')}"
        text_widget.tag_config(tag_name, foreground=color_hex)
        text_widget.insert(tk.END, msg, tag_name)
        text_widget.see(tk.END)

    def _ssh_worker(self, device: dict, commands: List[str], text_widget: scrolledtext.ScrolledText):
        """Hàm chạy luồng ngầm kết nối Netmiko để không làm treo giao diện UI."""
        try:
            from netmiko import ConnectHandler
        except ImportError:
            self.root.after(0, self._write_log, text_widget, "\n[❌] Lỗi: Thư viện 'netmiko' chưa được cài đặt!\n", "#f44747")
            self.root.after(0, self._write_log, text_widget, "    Hãy cài đặt bằng: pip install netmiko\n", "#dcdcaa")
            return

        try:
            self.root.after(0, self._write_log, text_widget, f"[*] Đang kết nối tới SSH {device['host']}...\n", "#dcdcaa")
            net_connect = ConnectHandler(**device)

            self.root.after(0, self._write_log, text_widget, "[✔] Kết nối SSH thành công! Đang chuyển sang mode enable...\n", "#4ec9b0")
            net_connect.enable()

            self.root.after(0, self._write_log, text_widget, "[*] Đang thực thi cấu hình lệnh CLI...\n", "#dcdcaa")
            output = net_connect.send_config_set(commands)
            self.root.after(0, self._write_log, text_widget, f"\n--- OUTPUT FROM SWITCH ---\n{output}\n--------------------------\n", "#9cdcfe")

            self.root.after(0, self._write_log, text_widget, "[*] Đang lưu cấu hình NVRAM (write memory)...\n", "#dcdcaa")
            save_out = net_connect.save_config()
            self.root.after(0, self._write_log, text_widget, f"{save_out}\n", "#9cdcfe")

            net_connect.disconnect()
            self.root.after(0, self._write_log, text_widget, "\n[✔] HOÀN TẤT THỰC THI THÀNH CÔNG!\n", "#4ec9b0")
            self.root.after(0, messagebox.showinfo, "Thành công", "Đã thực thi cấu hình trên Switch thành công!")

        except Exception as e:
            err_msg = f"\n[❌] Đã xảy ra lỗi khi kết nối SSH:\n{str(e)}\n"
            self.root.after(0, self._write_log, text_widget, err_msg, "#f44747")
            self.root.after(0, messagebox.showerror, "Lỗi kết nối", f"Không thể kết nối hoặc gửi lệnh tới Switch:\n{e}")


def main():
    root = tk.Tk()
    app = CiscoAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
