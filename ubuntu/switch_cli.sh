#!/usr/bin/env bash
# ==============================================================================
# VIRTUAL SWITCH CLI: CÔNG CỤ CẤU HÌNH VIRTUAL SWITCH TRỰC TIẾP
# ==============================================================================

function show_usage() {
    echo "Sử dụng:"
    echo "  sudo ./switch_cli.sh show                       : Hiển thị bảng VLAN trên Virtual Switch"
    echo "  sudo ./switch_cli.sh set-vlan <pc1|pc2|pc3> <vid> : Đổi Access VLAN cho một port trên Switch"
    echo ""
    echo "Ví dụ:"
    echo "  sudo ./switch_cli.sh set-vlan pc1 20   (Chuyển Cổng PC1 sang Access VLAN 20)"
}

case "$1" in
    show)
        echo "=== BẢNG CẤU HÌNH VLAN TRÊN VIRTUAL SWITCH br0 ==="
        bridge vlan show
        ;;
    set-vlan)
        pc="$2"
        vid="$3"
        if [ -z "$pc" ] || [ -z "$vid" ]; then
            show_usage
            exit 1
        fi
        port="veth-${pc}-sw"
        if ! ip link show "$port" >/dev/null 2>&1; then
            echo "Lỗi: Port $port không tồn tại trên Switch!"
            exit 1
        fi
        echo "Đang đổi Access VLAN của port $port sang VLAN $vid..."
        # Xóa tất cả vlan untagged cũ
        bridge vlan del dev "$port" vid 10 2>/dev/null || true
        bridge vlan del dev "$port" vid 20 2>/dev/null || true
        bridge vlan del dev "$port" vid 30 2>/dev/null || true
        bridge vlan del dev "$port" vid 1 2>/dev/null || true
        # Gán vlan mới
        bridge vlan add dev "$port" vid "$vid" pvid untagged
        echo "Thành công! Port $port hiện tại thuộc Access VLAN $vid."
        echo ""
        bridge vlan show dev "$port"
        ;;
    *)
        show_usage
        ;;
esac
