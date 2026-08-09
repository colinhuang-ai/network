#!/usr/bin/env bash
# ==============================================================================
# LAB MẠNG: DỌN DẸP SẠCH MÔ HÌNH LAB (TEARDOWN / CLEANUP)
# ==============================================================================

echo "Đang xóa các Virtual Nodes (Namespaces: pc1, pc2, pc3, router)..."
ip netns del pc1 2>/dev/null || true
ip netns del pc2 2>/dev/null || true
ip netns del pc3 2>/dev/null || true
ip netns del router 2>/dev/null || true

echo "Đang xóa Virtual Switch (br0)..."
ip link del br0 2>/dev/null || true

echo "Đã dọn dẹp sạch toàn bộ môi trường Lab mạng!"
