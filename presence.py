#!/usr/bin/env python3
"""
presence.py — Discord Rich Presence cho Botdis.

Hai chế độ:
  A) Chạy độc lập:      python presence.py
  B) Nhúng vào bot:     thêm "presence.py" vào PARTS trong main.py
                        -> presence tự bật trong thread nền khi bot chạy,
                           và có lệnh slash /presence để đổi nội dung.

Lệnh slash (khi nhúng vào bot):
  /presence status:<chữ>   đổi dòng chữ to (VD: "ĐANG XEM XXX")
  /presence note:<chữ>     đổi chú thích ảnh lớn
  /presence small:<chữ>    đổi chú thích ảnh nhỏ
  /presence anh:<ten>      đổi tên asset ảnh (phải upload trong Developer Portal)
  /presence reset:true     trả về mặc định
"""

import sys
import time
import threading

# Console Windows mặc định cp1252 không in được tiếng Việt -> ép sang UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ======================================================================
# >>>  PHẦN BẠN TỰ CHỈNH SỬA  <<<
# ======================================================================

# ID ứng dụng Discord (Developer Portal -> General Information -> Application ID)
# Phải trùng app của DISCORD_TOKEN trong .env thì tên activity mới đúng
RPC_CLIENT_ID = "1549735815171801128"

# Giá trị mặc định khi vừa bật
PRESENCE_DEFAULTS = {
    "details": "ĐANG XEM XXX",   # dòng chữ to, đậm
    "state": "",                 # dòng chữ nhỏ (để "" nếu không dùng)
    "large_text": "bá vương",    # chú thích ảnh lớn
    "small_text": "gay lọ",      # chú thích ảnh nhỏ
    "large_image": "",           # để trống; gửi ảnh qua /presence anh: để đặt
    "small_image": "",
}

# Bao lâu làm mới một lần (giây)
PRESENCE_REFRESH = 15

# ======================================================================
# >>>  LOGIC CHẠY — ít khi cần đụng  <<<
# ======================================================================

# Trạng thái hiện tại (thread đọc lại mỗi lần refresh,
# nên /presence đổi ở đây là lần refresh sau tự cập nhật)
PRESENCE_STATE = dict(PRESENCE_DEFAULTS)

_presence_thread = None


def _presence_build_payload():
    p = {
        "details": PRESENCE_STATE["details"],
        "start": int(time.time()),
        "large_image": PRESENCE_STATE["large_image"] or None,
        "large_text": PRESENCE_STATE["large_text"],
        "small_image": PRESENCE_STATE["small_image"] or None,
        "small_text": PRESENCE_STATE["small_text"],
    }
    if PRESENCE_STATE["state"]:
        p["state"] = PRESENCE_STATE["state"]
    return p


def _presence_rpc_loop():
    try:
        from pypresence import Presence
    except ImportError:
        print("[presence] Thiếu 'pypresence' -> bỏ qua presence. (pip install pypresence)")
        return
    try:
        rpc = Presence(RPC_CLIENT_ID)
        rpc.connect()
    except Exception as e:
        print(f"[presence] Không kết nối được Discord desktop: {e}")
        print("[presence] (Mở Discord bản cài trên máy rồi chạy lại. Bot vẫn chạy bình thường.)")
        return

    print("[presence] Đã kết nối Discord Rich Presence.")
    while True:
        try:
            rpc.update(**_presence_build_payload())
        except Exception as e:
            print(f"[presence] Mất kết nối, thử lại: {e}")
            try:
                rpc = Presence(RPC_CLIENT_ID)
                rpc.connect()
            except Exception:
                print("[presence] Dừng presence (Discord đã tắt?).")
                return
        time.sleep(PRESENCE_REFRESH)


def start_presence_thread():
    """Bật presence trong thread nền. An toàn gọi nhiều lần / gọi khi bot chạy."""
    global _presence_thread
    if _presence_thread is not None and _presence_thread.is_alive():
        return _presence_thread
    _presence_thread = threading.Thread(
        target=_presence_rpc_loop, daemon=True, name="presence"
    )
    _presence_thread.start()
    return _presence_thread


# ----------------------------------------------------------------------
# Khi được main.py exec vào namespace bot: tự bật thread presence.
# (Lệnh slash /presence nằm trong slash.py)
# ----------------------------------------------------------------------
if "bot" in globals():
    start_presence_thread()


# ----------------------------------------------------------------------
# Chạy độc lập
# ----------------------------------------------------------------------
def _presence_main():
    start_presence_thread()
    print("Presence đang chạy nền. Nhấn Ctrl+C để dừng.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nĐã dừng presence.")


if __name__ == "__main__":
    _presence_main()
