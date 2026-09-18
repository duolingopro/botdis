#!/usr/bin/env python3
# main.py — BÁ VƯƠNG ĐẠI ĐẾ v9.0 LOADER

import os
import sys

# Console Windows mặc định cp1252 không in được tiếng Việt -> ép sang UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_here = os.path.dirname(os.path.abspath(__file__))

# Thứ tự QUAN TRỌNG — đừng đổi
PARTS = [
    "start.py",         # 1. Config + DB + API + Bot init
    "core.py",          # 2. Roast VN gốc + Fake + Mirror + AFK
    "roast_vn.py",      # 3. Chửi VN (dùng forge_roast_vn)
    "voice.py",         # 4. Voice + Music + TTS
    "music_player.py",  # 5. Music Player + Lyrics
    "slash.py",         # 6. User-install Slash Commands
    "tools.py",         # 7. Tools (download, image, network, crypto, util)
    "presence.py",      # 8. Rich Presence + lệnh /presence
]

print("""
==================================================
       BÁ VƯƠNG ĐẠI ĐẾ v9.0
       Đang tải %d parts...
       [Tools · Music Player · Slash · Chửi VN]
==================================================
""" % len(PARTS))

shared = {
    "__name__": "bot_main",
    "__file__": os.path.join(_here, "main.py"),
}

for i, fname in enumerate(PARTS, 1):
    path = os.path.join(_here, fname)
    if not os.path.exists(path):
        print(f"❌ THIẾU FILE: {fname}")
        print(f"   Thư mục: {_here}")
        sys.exit(1)

    print(f"[{i}/{len(PARTS)}] {fname} ...")
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        exec(compile(code, path, "exec"), shared)
    except SyntaxError as e:
        print(f"\n❌ LỖI CÚ PHÁP trong {fname}:")
        print(f"   Dòng {e.lineno}: {e.msg}")
        print(f"   {e.text}")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\n❌ LỖI khi load {fname}: {e}")
        traceback.print_exc()
        sys.exit(1)

print("\n✅ Đã load %d parts.\n" % len(PARTS))

if "start_bot" not in shared:
    print("❌ Không tìm thấy start_bot() trong tools.py")
    sys.exit(1)

try:
    shared["start_bot"]()
except SystemExit:
    pass
except KeyboardInterrupt:
    print("\n👋 Đã thoát (Ctrl+C).")
except Exception as e:
    import traceback
    print(f"\n❌ LỖI KHI CHẠY BOT: {e}")
    traceback.print_exc()
    input("\nEnter để thoát...")