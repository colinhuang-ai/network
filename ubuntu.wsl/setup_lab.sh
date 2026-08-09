#!/usr/bin/env bash
# ==============================================================================
# LAB MẠNG: 3 VIRTUAL MACHINES (DOCKER), 3 VLANS, VIRTUAL SWITCH & VIRTUAL ROUTER
# ==============================================================================

set -e

echo "[1/6] Kiểm tra và khởi chạy dịch vụ Docker..."
service docker status >/dev/null 2>&1 || service docker start

echo "[2/6] Dọn dẹp môi trường cũ..."
umount -l /var/run/netns/pc1 /var/run/netns/pc2 /var/run/netns/pc3 /var/run/netns/router 2>/dev/null || true
rm -f /var/run/netns/pc1 /var/run/netns/pc2 /var/run/netns/pc3 /var/run/netns/router 2>/dev/null || true
docker rm -f pc1 pc2 pc3 router 2>/dev/null || true

ip link del veth-pc1-sw 2>/dev/null || true
ip link del veth-pc2-sw 2>/dev/null || true
ip link del veth-pc3-sw 2>/dev/null || true
ip link del veth-router-sw 2>/dev/null || true
ip link del br0 2>/dev/null || true

echo "[3/6] Khởi tạo 4 Docker Containers làm 3 Máy ảo (PC1, PC2, PC3) & 1 Router..."
docker run -d --name pc1 --net=none --privileged alpine sleep infinity
docker run -d --name pc2 --net=none --privileged alpine sleep infinity
docker run -d --name pc3 --net=none --privileged alpine sleep infinity
docker run -d --name router --net=none --privileged alpine sleep infinity

echo "[4/6] Khởi tạo Virtual Switch br0 (Linux Bridge với VLAN Filtering)..."
ip link add name br0 type bridge vlan_filtering 1
ip link set br0 up
bridge vlan del dev br0 vid 1 self 2>/dev/null || true

echo "[5/6] Kết nối card mạng ảo (veth pairs) vào Virtual Switch..."

PID_PC1=$(docker inspect -f '{{.State.Pid}}' pc1)
PID_PC2=$(docker inspect -f '{{.State.Pid}}' pc2)
PID_PC3=$(docker inspect -f '{{.State.Pid}}' pc3)
PID_ROUTER=$(docker inspect -f '{{.State.Pid}}' router)

mkdir -p /var/run/netns
ln -sf /proc/$PID_PC1/ns/net /var/run/netns/pc1
ln -sf /proc/$PID_PC2/ns/net /var/run/netns/pc2
ln -sf /proc/$PID_PC3/ns/net /var/run/netns/pc3
ln -sf /proc/$PID_ROUTER/ns/net /var/run/netns/router

# PC1 <-> Switch
ip link add eth0-pc1 type veth peer name veth-pc1-sw
ip link set eth0-pc1 netns pc1
ip link set veth-pc1-sw master br0
ip link set veth-pc1-sw up
ip netns exec pc1 ip link set lo up
ip netns exec pc1 ip link set eth0-pc1 up

# PC2 <-> Switch
ip link add eth0-pc2 type veth peer name veth-pc2-sw
ip link set eth0-pc2 netns pc2
ip link set veth-pc2-sw master br0
ip link set veth-pc2-sw up
ip netns exec pc2 ip link set lo up
ip netns exec pc2 ip link set eth0-pc2 up

# PC3 <-> Switch
ip link add eth0-pc3 type veth peer name veth-pc3-sw
ip link set eth0-pc3 netns pc3
ip link set veth-pc3-sw master br0
ip link set veth-pc3-sw up
ip netns exec pc3 ip link set lo up
ip netns exec pc3 ip link set eth0-pc3 up

# Router <-> Switch
ip link add eth0-router type veth peer name veth-router-sw
ip link set eth0-router netns router
ip link set veth-router-sw master br0
ip link set veth-router-sw up
ip netns exec router ip link set lo up
ip netns exec router ip link set eth0-router up

echo "[6/6] CẤU HÌNH VLAN TRỰC TIẾP TRÊN SWITCH & ROUTER..."

# Access Ports
bridge vlan del dev veth-pc1-sw vid 1 2>/dev/null || true
bridge vlan del dev veth-pc2-sw vid 1 2>/dev/null || true
bridge vlan del dev veth-pc3-sw vid 1 2>/dev/null || true
bridge vlan del dev veth-router-sw vid 1 2>/dev/null || true

bridge vlan add dev veth-pc1-sw vid 10 pvid untagged
bridge vlan add dev veth-pc2-sw vid 20 pvid untagged
bridge vlan add dev veth-pc3-sw vid 30 pvid untagged

# Trunk Port
bridge vlan add dev veth-router-sw vid 10
bridge vlan add dev veth-router-sw vid 20
bridge vlan add dev veth-router-sw vid 30

# IP PC1, PC2, PC3
docker exec pc1 ip addr add 192.168.10.10/24 dev eth0-pc1
docker exec pc1 ip route add default via 192.168.10.1

docker exec pc2 ip addr add 192.168.20.10/24 dev eth0-pc2
docker exec pc2 ip route add default via 192.168.20.1

docker exec pc3 ip addr add 192.168.30.10/24 dev eth0-pc3
docker exec pc3 ip route add default via 192.168.30.1

# Router Sub-interfaces 802.1Q
docker exec router ip link add link eth0-router name eth0-router.10 type vlan id 10
docker exec router ip link add link eth0-router name eth0-router.20 type vlan id 20
docker exec router ip link add link eth0-router name eth0-router.30 type vlan id 30

docker exec router ip link set eth0-router.10 up
docker exec router ip link set eth0-router.20 up
docker exec router ip link set eth0-router.30 up

docker exec router ip addr add 192.168.10.1/24 dev eth0-router.10
docker exec router ip addr add 192.168.20.1/24 dev eth0-router.20
docker exec router ip addr add 192.168.30.1/24 dev eth0-router.30

# Enable IP forwarding
docker exec router sysctl -w net.ipv4.ip_forward=1 >/dev/null

echo "=========================================================================="
echo " KHỞI TẠO LAB THÀNH CÔNG!"
echo " - 3 Máy ảo (Docker): pc1 (VLAN 10), pc2 (VLAN 20), pc3 (VLAN 30)"
echo " - Virtual Switch br0: Access Ports & Trunk Port"
echo " - Virtual Router: Inter-VLAN Gateway (192.168.x.1)"
echo "=========================================================================="
