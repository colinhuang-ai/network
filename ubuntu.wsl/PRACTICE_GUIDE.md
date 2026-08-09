# HƯỚNG DẪN THỰC HÀNH MẠNG: 3 VIRTUAL MACHINES, 3 VLANS, SWITCH & ROUTER

Tài liệu duy nhất hướng dẫn thực hành lab mạng trên **Ubuntu WSL2**. Môi trường giả lập gồm **3 Máy ảo (PC1, PC2, PC3)** thuộc 3 VLAN riêng biệt, kết nối qua **Virtual Switch** (cấu hình Access/Trunk ports trực tiếp) và **Virtual Router** (Inter-VLAN Gateway).

---

## 1. Các lệnh Quản lý Lab Cơ bản

Thư mục làm việc: `d:\Training\2026-08_networking\network\ubuntu.wsl` (hoặc `/mnt/d/Training/2026-08_networking/network/ubuntu.wsl`).

| Thao tác | Lệnh chạy (với quyền root trong Ubuntu WSL) |
| :--- | :--- |
| **1. Khởi tạo / Reset toàn bộ Lab** | `sudo ./setup_lab.sh` |
| **2. Xem trạng thái Máy ảo & VLAN** | `sudo ./status_lab.sh` |
| **3. Xem bảng VLAN của Switch** | `sudo ./switch_cli.sh show` |
| **4. Đổi VLAN cổng Switch (PC1)** | `sudo ./switch_cli.sh set-vlan pc1 20` |
| **5. Dọn dẹp sạch khi dừng lab** | `sudo ./destroy_lab.sh` |

---

## 2. Cách truy cập vào Terminal từng Máy ảo

Mỗi máy ảo chạy cực nhẹ dưới dạng Docker Container (~5MB RAM). Bạn có thể mở Shell trực tiếp inside từng máy như SSH vào máy thật:

- **Vào máy ảo PC1 (VLAN 10)**: `docker exec -it pc1 sh`
- **Vào máy ảo PC2 (VLAN 20)**: `docker exec -it pc2 sh`
- **Vào máy ảo PC3 (VLAN 30)**: `docker exec -it pc3 sh`
- **Vào Virtual Router**: `docker exec -it router sh`
*(Gõ `exit` để thoát khỏi máy ảo về Ubuntu WSL).*

---

## 3. BÀI TẬP THỰC HÀNH MẠNG (LAB EXERCISES)

### Bài tập 1: Kiểm tra Ping & Định tuyến Inter-VLAN
1. **Ping từ PC1 (VLAN 10) tới Gateway**:
   ```bash
   docker exec -it pc1 ping -c 3 192.168.10.1
   ```
2. **Ping liên VLAN (Từ PC1 ở VLAN 10 sang PC2 ở VLAN 20)**:
   ```bash
   docker exec -it pc1 ping -c 3 192.168.20.10
   ```
   *(Thành công! TTL = 63 chứng tỏ gói tin đã đi qua Router).*
3. **Tracing đường đi gói tin với `traceroute`**:
   ```bash
   docker exec -it pc1 traceroute 192.168.30.10
   ```

---

### Bài tập 2: Thay đổi VLAN trên Virtual Switch & Kiểm tra Cách ly Mạng
1. **Đổi cổng của PC1 từ Access VLAN 10 sang Access VLAN 20**:
   ```bash
   sudo ./switch_cli.sh set-vlan pc1 20
   ```
2. **Thử ping lại Gateway `192.168.10.1` từ PC1**:
   ```bash
   docker exec -it pc1 ping -c 3 192.168.10.1
   ```
   *(Thất bại! Vì Switch hiện coi PC1 thuộc VLAN 20 nên chặn không cho sang dải 10.1).*
3. **Trả PC1 về lại VLAN 10**:
   ```bash
   sudo ./switch_cli.sh set-vlan pc1 10
   ```

---

### Bài tập 3: Bắt gói tin (Packet Capture) xem tiêu đề 802.1Q VLAN Tagging
1. Chạy `tcpdump` trên cổng Trunk kết nối giữa Switch và Router:
   ```bash
   docker exec -it router tcpdump -i eth0-router -e -n vlan
   ```
2. Trong terminal khác, phát lệnh ping từ PC1 (VLAN 10) tới PC3 (VLAN 30):
   ```bash
   docker exec -it pc1 ping -c 2 192.168.30.10
   ```
   *Quan sát màn hình tcpdump thấy rõ thông tin `vlan 10` và `vlan 30`.*
