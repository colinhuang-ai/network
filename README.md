# Tự Động Hóa Quản Lý Cấu Hình Cisco Switch Bằng Python

Bộ script Python và ứng dụng giao diện Desktop tự động hóa việc cấu hình Cisco Switch trong môi trường doanh nghiệp:
1. **`app_gui.py`**: **Giao diện Desktop UI trực quan** quản lý cả 2 tác vụ dưới đây.
2. **`initial_config.py`**: Thực hiện toàn bộ cấu hình ban đầu cho Switch (VLANs, Access Port Ranges, Trunk Port).
3. **`add_employee.py`**: Cấu hình cổng mạng và VLAN khi có 1 nhân viên mới vào làm.

---

## 🖥️ Khởi Chạy Giao Diện Desktop UI

Để mở ứng dụng Desktop UI trực quan:
```bash
python app_gui.py
```
Giao diện bao gồm:
- **Tab 1 (Cấu hình ban đầu)**: Nhập IP/Tài khoản Switch, xem trước câu lệnh CLI (Dry-Run) hoặc thực thi trực tiếp.
- **Tab 2 (Cấp cổng nhân viên mới)**: Nhập tên nhân viên, chọn VLAN (Admin, Guest, Staff), chọn Cổng Switch (Port) và bấm cấp phát.
- **Tab 3 (Thông tin VLAN)**: Xem bảng quản lý các VLAN và phân dải cổng mặc định.

---


## 🛠️ Requirements & Cài Đặt

### 1. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```
*(Nếu chưa kết nối thiết bị thật, các script hỗ trợ tham số `--dry-run` để chạy giả lập in câu lệnh mà không cần thư viện `netmiko`)*.

### 2. Cấu hình thông số kết nối (`config.py`)
Mặc định script đọc thông tin kết nối từ file [config.py](file:///d:/Training/2026-08_networking/network/config.py) hoặc qua các biến môi trường:
- **IP Switch**: `192.168.1.2` (biến `SWITCH_HOST`)
- **Username**: `admin` (biến `SWITCH_USER`)
- **Password**: `cisco123` (biến `SWITCH_PASS`)
- **Enable Secret**: `cisco123` (biến `SWITCH_SECRET`)

---

## 🚀 1. Chạy Cấu Hình Ban Đầu (`initial_config.py`)

Script này sẽ tự động khởi tạo:
- **VLAN 10** (Admin - Lễ tân / Quản lý) -> Cổng `fa0/1-5`
- **VLAN 20** (Guest - WiFi / Khách) -> Cổng `fa0/6-15`
- **VLAN 30** (Staff - Thiết bị Nhân viên) -> Cổng `fa0/16-24`
- **Trunk Port** -> Cổng `g0/1` nối tới Router
- Lưu cấu hình vào NVRAM (`write memory`)

### Chạy ở chế độ giả lập (Dry-Run):
```bash
python initial_config.py --dry-run
```

### Chạy trực tiếp kết nối tới Switch thật:
```bash
python initial_config.py --host 192.168.1.2 --user admin --password cisco123 --secret cisco123
```

---

## 👤 2. Chạy Khi Có Nhân Viên Mới Vào Làm (`add_employee.py`)

Script giúp gán cổng Switch, phân VLAN, đặt `description` nhận diện nhân viên và bật cổng `no shutdown`.

### Chế độ nhập tương tác (Interactive Mode):
```bash
python add_employee.py --dry-run
```
Hệ thống sẽ hiển thị menu hỏi tên nhân viên, phòng ban, chọn VLAN và cổng mạng tương ứng.

### Chế độ truyền tham số trực tiếp (Command Line Arguments):
```bash
python add_employee.py --name "Nguyen Van A" --dept "Marketing" --vlan 30 --port "fa0/18" --dry-run
```

---

## 📁 Cấu Trúc Thư Mục Project
```text
network/
├── config.py             # File cấu hình thông số Switch & danh sách VLAN
├── initial_config.py     # Script cấu hình ban đầu
├── add_employee.py       # Script cấp phát port cho nhân viên mới
├── requirements.txt      # Thư viện phụ thuộc Python
├── README.md             # Hướng dẫn sử dụng
└── switch/               # Thư mục chứa các file lệnh CLI tham khảo
    ├── vlan.cli
    ├── topc.cli
    └── trunk-router
```
