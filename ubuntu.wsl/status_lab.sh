#!/usr/bin/env bash
# ==============================================================================
# LAB MẠNG: KIỂM TRA TRẠNG THÁI (CONTAINERS, VLAN TABLE & IP ADDRESSES)
# ==============================================================================

echo "=========================================================================="
echo " 1. DANH SÁCH MÁY ÁO (DOCKER CONTAINERS)"
echo "=========================================================================="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

echo ""
echo "=========================================================================="
echo " 2. BẢNG CẤU HÌNH VLAN TRÊN VIRTUAL SWITCH (br0)"
echo "=========================================================================="
bridge vlan show

echo ""
echo "=========================================================================="
echo " 3. ĐỊA CHỈ IP TRÊN CÁC MÁY ÁO (PC1, PC2, PC3)"
echo "=========================================================================="
echo "--- PC1 (VLAN 10) ---"
docker exec pc1 ip -4 addr show dev eth0-pc1 | grep inet || echo "N/A"
echo "--- PC2 (VLAN 20) ---"
docker exec pc2 ip -4 addr show dev eth0-pc2 | grep inet || echo "N/A"
echo "--- PC3 (VLAN 30) ---"
docker exec pc3 ip -4 addr show dev eth0-pc3 | grep inet || echo "N/A"

echo ""
echo "=========================================================================="
echo " 4. VIRTUAL ROUTER - SUB-INTERFACES & IP GATEWAYS"
echo "=========================================================================="
docker exec router ip -4 addr show | grep inet || echo "N/A"
echo "=========================================================================="
