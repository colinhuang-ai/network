# HƯỚNG DẪN THỰC HÀNH MẠNG (VLAN, VIRTUAL SWITCH & ROUTER) TRÊN UBUNTU WSL2

Tài liệu hướng dẫn chi tiết cách thực hành các bài tập mạng với môi trường 3 Máy ảo (VM1, VM2, VM3), 3 VLAN (VLAN 10, 20, 30), Virtual Switch và Virtual Router vừa được cài đặt.

---

## 1. Các lệnh Quản lý Lab Cơ bản

Tất cả kịch bản được đặt tại thư mục: `d:\Training\2026-08_networking\network` (hoặc `/mnt/d/Training/2026-08_networking/network` trên WSL2).

| Thao tác | Lệnh chạy (chạy với quyền root trong Ubuntu WSL) |
| :--- | :--- |
| **Khởi tạo lại toàn bộ Lab** | `sudo ./setup_lab.sh` |
| **Xem trạng thái VLAN & IP** | `sudo ./status_lab.sh` |
| **Xem bảng VLAN của Switch** | `sudo ./switch_cli.sh show` |
| **Đổi VLAN cho 1 máy ảo** | `sudo ./switch_cli.sh set-vlan pc1 20` |
| **Xóa sạch Lab khi dừng** | `sudo ./destroy_lab.sh` |

---

## 2. BÀI TẬP THỰC HÀNH (LAB EXERCISES)

### Bài tập 1: Kiểm tra kết nối Ping & Định tuyến Inter-VLAN

#### Bước 1.1: Kiểm tra ping từ PC1 (VLAN 10) tới Gateway
Chạy lệnh từ Ubuntu WSL:
```bash
sudo ip netns exec pc1 ping -c 4 192.168.10.1
```
*Kết quả:* Ping thành công vì PC1 thuộc VLAN 10 và Gateway VLAN 10 là `192.168.10.1`.

#### Bước 1.2: Kiểm tra Inter-VLAN Routing (Từ PC1 ở VLAN 10 ping sang PC2 ở VLAN 20)
```bash
sudo ip netns exec pc1 ping -c 4 192.168.20.10
```
*Kết quả:* Ping thành công! Gói tin từ PC1 (192.168.10.10) đi qua Access Port VLAN 10 trên Switch -> lên Trunk Port (gắn VLAN Tag 10) -> vào Router sub-interface `eth-r.10` -> Router định tuyến sang `eth-r.20` -> qua Trunk Port (gắn VLAN Tag 20) -> Switch đẩy ra Access Port VLAN 20 -> đến PC2 (192.168.20.10).

#### Bước 1.3: Tracing đường đi của gói tin với `traceroute`
```bash
sudo ip netns exec pc1 traceroute 192.168.30.10
```
*Kết quả:* Thấy rõ hop đầu tiên đi qua Router (`192.168.10.1`), hop 2 tới PC3 (`192.168.30.10`).

---

### Bài tập 2: Thực hành Thay đổi VLAN tại Virtual Switch & Quan sát sự cách ly

Bây giờ bạn sẽ giả lập hành động **đổi VLAN của Port trên Switch** bằng công cụ `switch_cli.sh`.

#### Bước 2.1: Chuyển Cổng PC1 từ VLAN 10 sang VLAN 20
```bash
sudo ./switch_cli.sh set-vlan pc1 20
```

#### Bước 2.2: Thử ping lại Gateway cũ (192.168.10.1) từ PC1
```bash
sudo ip netns exec pc1 ping -c 3 192.168.10.1
```
*Kết quả:* **Destination Host Unreachable** hoặc **Timeout**!
*Giải thích:* Vì Switch hiện tại đã coi PC1 thuộc VLAN 20. Khi PC1 gửi gói tin ARP request cho `192.168.10.1`, Switch gán tag VLAN 20 nên gói tin chỉ gửi lên Router interface `eth-r.20` (thuộc dải 192.168.20.0/24), Router không nhận diện được IP 10.1 trên VLAN 20.

#### Bước 2.3: Trả lại PC1 về VLAN 10
```bash
sudo ./switch_cli.sh set-vlan pc1 10
```
Kiểm tra ping lại: `sudo ip netns exec pc1 ping -c 2 192.168.10.1` -> Đã thông trở lại!

---

### Bài tập 3: Bắt gói tin (Packet Capture) xem 802.1Q VLAN Tagging với `tcpdump`

Lệnh `tcpdump` cho phép bạn nhìn thấy thực sự tiêu đề (header) 802.1Q mang thông tin VLAN ID trên cổng Trunk kết nối giữa Switch và Router.

#### Bước 3.1: Mở cửa sổ bắt gói tin trên Trunk Port
Chạy trong WSL:
```bash
sudo ip netns exec router tcpdump -i veth-router -e -n vlan
```

#### Bước 3.2: Trong một terminal khác (hoặc lệnh song song), phát lệnh ping từ PC1 (VLAN 10) tới PC3 (VLAN 30):
```bash
sudo ip netns exec pc1 ping -c 2 192.168.30.10
```

#### Quan sát kết quả tcpdump:
Bạn sẽ thấy thông tin dòng gói tin chứa:
`vlan 10, p 0, ICMP echo request` và `vlan 30, p 0, ICMP echo request`!
Điều này chứng minh tiêu đề VLAN Tag 802.1Q đang hoạt động trực tiếp trên Virtual Switch và Router.

---

### Bài tập 4: Cấu hình Firewall / ACL trên Virtual Router ngăn chặn liên kết giữa các VLAN

Giả sử bạn muốn **VLAN 10 (Phòng Kế toán)** không được kết nối tới **VLAN 30 (Phòng Server)**, nhưng vẫn cho phép VLAN 20 truy cập.

#### Bước 4.1: Đặt quy tắc `iptables` trên Virtual Router
```bash
sudo ip netns exec router iptables -A FORWARD -s 192.168.10.0/24 -d 192.168.30.0/24 -j DROP
```

#### Bước 4.2: Kiểm tra kết nối từ PC1 (VLAN 10) sang PC3 (VLAN 30)
```bash
sudo ip netns exec pc1 ping -c 3 192.168.30.10
```
*Kết quả:* **Packet Filtered / Timeout** (bị chặn hoàn toàn bởi Router Firewall).

#### Bước 4.3: Kiểm tra kết nối từ PC2 (VLAN 20) sang PC3 (VLAN 30)
```bash
sudo ip netns exec pc2 ping -c 3 192.168.30.10
```
*Kết quả:* Ping vẫn **Thành công**!

#### Bước 4.4: Xóa quy tắc Firewall trên Router
```bash
sudo ip netns exec router iptables -F FORWARD
```

---

## 3. Tổng kết Lệnh mở Shell trực tiếp vào từng "Máy ảo"

Để gõ lệnh trực tiếp bên trong từng Máy ảo như thể bạn đang mở Terminal của máy ảo đó:

- **Mở Shell vào PC1**:
  ```bash
  sudo ip netns exec pc1 bash
  ```
- **Mở Shell vào Virtual Router**:
  ```bash
  sudo ip netns exec router bash
  ```
- Thoát khỏi máy ảo gõ: `exit`
