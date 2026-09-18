#!/usr/bin/env python3
# fix_all.py — Fix alias conflict trong tools.py
import os, re, shutil, sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "tools.py")

if not os.path.exists(PATH):
    print(f"❌ Không thấy: {PATH}")
    sys.exit(1)

print(f"📂 Đang xử lý: {PATH}")
with open(PATH, "r", encoding="utf-8") as f:
    code = f.read()

original_len = len(code)
changes = []

# === FIX 1: !ping → !pinghost ===
p1 = r'@bot\.command\(name="ping",\s*aliases=\["pinghost"\]\)\s*\nasync def cmd_ping\(ctx,\s*host:\s*str\s*=\s*None\):'
r1 = '@bot.command(name="pinghost", aliases=["hostping", "icmp"])\nasync def cmd_pinghost(ctx, host: str = None):'
code, n = re.subn(p1, r1, code)
if n:
    changes.append(f"  ✅ !ping → !pinghost ({n} chỗ)")

# Fallback ping
if "name=\"ping\"" in code and n == 0:
    code, n2 = re.subn(
        r'@bot\.command\(name="ping"[^\n]*\)\s*\nasync def cmd_ping\(',
        '@bot.command(name="pinghost", aliases=["hostping", "icmp"])\nasync def cmd_pinghost(',
        code
    )
    if n2:
        changes.append(f"  ✅ !ping → !pinghost fallback ({n2} chỗ)")

# === FIX 2: !short bỏ alias tiktok ===
p2 = r'@bot\.command\(name="short",\s*aliases=\["shorts",\s*"tiktok"\]\)'
r2 = '@bot.command(name="shorts", aliases=["yt"])'
code, n = re.subn(p2, r2, code)
if n:
    changes.append(f"  ✅ !short[tiktok] → !shorts ({n} chỗ)")

# Fallback short
if '"short"' in code and n == 0:
    code, n2 = re.subn(
        r'@bot\.command\(name="short"[^\n]*\)',
        '@bot.command(name="shorts", aliases=["yt"])',
        code
    )
    if n2:
        changes.append(f"  ✅ !short → !shorts fallback ({n2} chỗ)")

# Đổi tên hàm short → shorts
code, n = re.subn(r'async def cmd_short\(', 'async def cmd_shorts(', code)
if n:
    changes.append(f"  ✅ cmd_short → cmd_shorts ({n} chỗ)")

# === FIX 3: Update help text ===
old_help = '("!ping <host>", "Ping"),'
new_help = '("!pinghost <host>", "Ping host (ICMP)"),'
if old_help in code:
    code = code.replace(old_help, new_help)
    changes.append("  ✅ Update help ping")

old_help2 = '("!short", "Short video"),'
if old_help2 in code:
    code = code.replace(old_help2, '("!shorts", "YT Short"),')
    changes.append("  ✅ Update help shorts")

# === Check những command khác có alias tiktok ===
extra_fixes = []
# !tiktok có alias tiktokdl — OK, giữ
# Nếu có alias nào khác bị trùng thì báo

# === Backup ===
bak = PATH + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(PATH, bak)
print(f"💾 Backup: {os.path.basename(bak)}")

# === Save ===
with open(PATH, "w", encoding="utf-8") as f:
    f.write(code)

print()
if changes:
    for c in changes:
        print(c)
    print(f"\n✅ Đã patch ({original_len - len(code)} ký tự diff)")
else:
    print("⚠️ Không có gì thay đổi.")
    print("   Check thủ công: tìm dòng có `name=\"short\"` hoặc `name=\"ping\"` trong tools.py")

print("\n👉 Chạy lại: python main.py")