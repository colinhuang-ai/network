#!/usr/bin/env bash
# ==============================================================================
# LAB MẠNG: DỌN DẸP SẠCH TOÀN BỘ MÔ HÌNH LAB
# ==============================================================================

echo "Đang dừng và xóa các Máy ảo (pc1, pc2, pc3, router)..."
umount -l /var/run/netns/pc1 /var/run/netns/pc2 /var/run/netns/pc3 /var/run/netns/router 2>/dev/null || true
rm -f /var/run/netns/pc1 /var/run/netns/pc2 /var/run/netns/pc3 /var/run/netns/router 2>/dev/null || true
docker rm -f pc1 pc2 pc3 router 2>/dev/null || true

echo "Đang xóa Virtual Switch (br0)..."
ip link del br0 2>/dev/null || true

echo "Đã dọn dẹp sạch toàn bộ môi trường Lab!"
