#!/usr/bin/env bash
# ==============================================================================
# LAB MẠNG: 3 VIRTUAL MACHINES, 3 VLANS, VIRTUAL SWITCH & VIRTUAL ROUTER IN WSL
# ==============================================================================

set -e

echo "[1/6] Dọn dẹp môi trường cũ (nếu có)..."
ip netns del pc1 2>/dev/null || true
ip netns del pc2 2>/dev/null || true
ip netns del pc3 2>/dev/null || true
ip netns del router 2>/dev/null || true
ip link del br0 2>/dev/null || true

echo "[2/6] Khởi tạo 4 Virtual Nodes (Namespaces: pc1, pc2, pc3, router)..."
ip netns add pc1
ip netns add pc2
ip netns add pc3
ip netns add router

# Bật interface loopback trong từng namespace
ip netns exec pc1 ip link set lo up
ip netns exec pc2 ip link set lo up
ip netns exec pc3 ip link set lo up
ip netns exec router ip link set lo up

echo "[3/6] Khởi tạo Virtual Switch br0 (Linux Bridge với VLAN Filtering)..."
ip link add name br0 type bridge vlan_filtering 1
ip link set br0 up

# Xóa VLAN 1 mặc định trên br0 nếu cần hoặc cấu hình lại
bridge vlan del dev br0 vid 1 self 2>/dev/null || true

echo "[4/6] Tạo các Virtual Ethernet Cable (veth pairs) kết nối PCs & Router vào Switch..."

# veth pair cho PC1 <-> Switch
ip link add veth-pc1 type veth peer name veth-pc1-sw
ip link set veth-pc1 netns pc1
ip link set veth-pc1-sw master br0

# veth pair cho PC2 <-> Switch
ip link add veth-pc2 type veth peer name veth-pc2-sw
ip link set veth-pc2 netns pc2
ip link set veth-pc2-sw master br0

# veth pair cho PC3 <-> Switch
ip link add veth-pc3 type veth peer name veth-pc3-sw
ip link set veth-pc3 netns pc3
ip link set veth-pc3-sw master br0

# veth pair cho Router <-> Switch
ip link add veth-router type veth peer name veth-router-sw
ip link set veth-router netns router
ip link set veth-router-sw master br0

# Bật tất cả các switch ports
ip link set veth-pc1-sw up
ip link set veth-pc2-sw up
ip link set veth-pc3-sw up
ip link set veth-router-sw up

# Bật các card mạng phía PC và Router
ip netns exec pc1 ip link set veth-pc1 up
ip netns exec pc2 ip link set veth-pc2 up
ip netns exec pc3 ip link set veth-pc3 up
ip netns exec router ip link set veth-router up

echo "[5/6] CẤU HÌNH VLAN TRỰC TIẾP TRÊN VIRTUAL SWITCH (Access Ports & Trunk Port)..."

# Xóa VLAN 1 mặc định trên các switch ports
bridge vlan del dev veth-pc1-sw vid 1 2>/dev/null || true
bridge vlan del dev veth-pc2-sw vid 1 2>/dev/null || true
bridge vlan del dev veth-pc3-sw vid 1 2>/dev/null || true
bridge vlan del dev veth-router-sw vid 1 2>/dev/null || true

# Port 1 (PC1): ACCESS PORT - VLAN 10 (Gán pvid 10 untagged)
bridge vlan add dev veth-pc1-sw vid 10 pvid untagged

# Port 2 (PC2): ACCESS PORT - VLAN 20 (Gán pvid 20 untagged)
bridge vlan add dev veth-pc2-sw vid 20 pvid untagged

# Port 3 (PC3): ACCESS PORT - VLAN 30 (Gán pvid 30 untagged)
bridge vlan add dev veth-pc3-sw vid 30 pvid untagged

# Port 4 (Router): TRUNK PORT - Cho phép Tagged VLAN 10, 20, 30 đi qua
bridge vlan add dev veth-router-sw vid 10
bridge vlan add dev veth-router-sw vid 20
bridge vlan add dev veth-router-sw vid 30

echo "[6/6] Cấu hình địa chỉ IP cho 3 PC và Sub-interfaces (802.1Q) trên Router..."

# PC1: 192.168.10.10/24 (VLAN 10)
ip netns exec pc1 ip addr add 192.168.10.10/24 dev veth-pc1
ip netns exec pc1 ip route add default via 192.168.10.1

# PC2: 192.168.20.10/24 (VLAN 20)
ip netns exec pc2 ip addr add 192.168.20.10/24 dev veth-pc2
ip netns exec pc2 ip route add default via 192.168.20.1

# PC3: 192.168.30.10/24 (VLAN 30)
ip netns exec pc3 ip addr add 192.168.30.10/24 dev veth-pc3
ip netns exec pc3 ip route add default via 192.168.30.1

# Router: Tạo sub-interfaces 802.1Q cho VLAN 10, 20, 30
ip netns exec router ip link add link veth-router name veth-router.10 type vlan id 10
ip netns exec router ip link add link veth-router name veth-router.20 type vlan id 20
ip netns exec router ip link add link veth-router name veth-router.30 type vlan id 30

ip netns exec router ip link set veth-router.10 up
ip netns exec router ip link set veth-router.20 up
ip netns exec router ip link set veth-router.30 up

# Gán địa chỉ Gateway trên Router
ip netns exec router ip addr add 192.168.10.1/24 dev veth-router.10
ip netns exec router ip addr add 192.168.20.1/24 dev veth-router.20
ip netns exec router ip addr add 192.168.30.1/24 dev veth-router.30

# Bật IP Forwarding trên Virtual Router
ip netns exec router sysctl -w net.ipv4.ip_forward=1 >/dev/null

echo "=========================================================================="
echo " KHỞI TẠO LAB THÀNH CÔNG!"
echo " - Virtual Switch br0: Đã cấu hình Access Ports (VLAN 10, 20, 30) & Trunk Port."
echo " - Virtual Router: Đã bật IP Forwarding và gán Gateway 192.168.x.1."
echo " - 3 Virtual Nodes: PC1 (192.168.10.10), PC2 (192.168.20.10), PC3 (192.168.30.10)."
echo "=========================================================================="
