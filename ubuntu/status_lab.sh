#!/usr/bin/env bash
# ==============================================================================
# LAB MẠNG: KIỂM TRA TRẠNG THÁI LAB (VLAN TABLE, IP ADDRESSES, ROUTING)
# ==============================================================================

echo "=========================================================================="
echo " 1. BẢNG CẤU HÌNH VLAN TRÊN VIRTUAL SWITCH (br0)"
echo "=========================================================================="
bridge vlan show

echo ""
echo "=========================================================================="
echo " 2. DANH SÁCH MÁY ÁO & ĐỊA CHỈ IP (PC1, PC2, PC3)"
echo "=========================================================================="
echo "--- PC1 (VLAN 10) ---"
ip netns exec pc1 ip -4 addr show dev veth-pc1 | grep inet || echo "Chưa có IP"
echo "--- PC2 (VLAN 20) ---"
ip netns exec pc2 ip -4 addr show dev veth-pc2 | grep inet || echo "Chưa có IP"
echo "--- PC3 (VLAN 30) ---"
ip netns exec pc3 ip -4 addr show dev veth-pc3 | grep inet || echo "Chưa có IP"

echo ""
echo "=========================================================================="
echo " 3. VIRTUAL ROUTER - SUB-INTERFACES & IP GATEWAYS"
echo "=========================================================================="
ip netns exec router ip -4 addr show | grep inet || echo "Chưa có IP"

echo ""
echo "=========================================================================="
echo " 4. TRẠNG THÁI CHUYỂN TIẾP IP (IP FORWARDING ON ROUTER)"
echo "=========================================================================="
sysctl_val=$(ip netns exec router sysctl -n net.ipv4.ip_forward 2>/dev/null || echo "0")
if [ "$sysctl_val" = "1" ]; then
    echo "net.ipv4.ip_forward = 1 [ENABLED - ROUTER IS ACTIVE]"
else
    echo "net.ipv4.ip_forward = 0 [DISABLED]"
fi
echo "=========================================================================="
