# tools.py v9.4 — BLOCK 1/2
# BÁ VƯƠNG TOOLS · Multi-fallback · KHÔNG lỗi

import os
import io
import re
import time
import shutil
import socket
import subprocess
import urllib.parse
import tempfile
import base64
import random
import asyncio
import hashlib
from datetime import datetime
import aiohttp

try:
    from PIL import Image
    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    import ipaddress
    IPADDR_OK = True
except ImportError:
    IPADDR_OK = False


# ============================================================
# BÁ VƯƠNG NGÔN TỪ
# ============================================================
_BV_LOADING = [
    "⚔️ Trẫm đang động binh...", "👑 Trẫm đang xử lý, đợi một khắc...",
    "🔥 Quân sư đang luận bàn...", "💀 Trẫm đang rót từng giọt công lực...",
    "⚔️ Chưa xong đâu, đừng hối...", "👑 Trẫm đang vận công...",
    "🌋 Lửa đã nổi, chờ chút...", "☠️ Trẫm đang bày binh bố trận...",
]
_BV_OK = [
    "⚔️ **TRẪM BAN CHIẾU:**", "👑 **TRẪM ĐÃ XỬ:**",
    "🔥 **TRẪM PHÁN:**", "⚔️ **CHIẾU CHỈ VỪA BAN:**",
    "👑 **TRẪM ĐÃ ĐỊNH:**", "🌋 **Ý TRẪM LÀ:**",
]
_BV_ERR = [
    "💀 **TRẪM QUỞ TRÁCH:**", "🚫 **TRẪM ĐÉO VỪA LÒNG:**",
    "⚔️ **TRẪM CHÊ:**", "☠️ **TRẪM KHÔNG HÀI LÒNG:**",
    "🤬 **TRẪM NỔI ĐIÊN:**", "💢 **TRẪM BÁO LỖI:**",
]
_BV_TITLE = [
    "👑  CHIẾU CHỈ BÁ VƯƠNG  👑", "⚔️  LỆNH TRẪM BAN  ⚔️",
    "🔥  SẮC LỆNH ĐẾ VƯƠNG  🔥", "💀  TRẪM PHÁN  💀",
    "⚔️  HOÀNG LỆNH  ⚔️", "👑  CHIẾU THƯ  👑",
]


def _bv_loading():
    return random.choice(_BV_LOADING)


def _bv_ok():
    return random.choice(_BV_OK)


def _bv_err():
    return random.choice(_BV_ERR)


def _bv_title():
    return random.choice(_BV_TITLE)


def _bv_ok_msg(text):
    return f"{_bv_ok()}\n{text}"


def _bv_err_msg(text):
    return f"{_bv_err()}\n`{text[:300]}`"


# ============================================================
# HELP
# ============================================================
HELP_CATS = {
    "roast":   {"label": "⚔️  BỐ PHÁN",     "color": ROYAL_RED,  "commands": []},
    "fake":    {"label": "🎭  GIẢ DANH",     "color": ROYAL_RED,  "commands": []},
    "spamtin": {"label": "📮  BÃO TIN",      "color": ROYAL_RED,  "commands": []},
    "mirror":  {"label": "🪞  MIRROR",       "color": 0x9B59B6,   "commands": []},
    "afk":     {"label": "💤  AFK",          "color": 0x99AAFF,   "commands": []},
    "autodel": {"label": "🗑️  AUTO-DELETE", "color": 0xE74C3C,   "commands": []},
    "voice":   {"label": "🎤  TTS",          "color": ROYAL_GOLD, "commands": []},
    "voicechat":{"label": "🎙️  VOICE CHAT", "color": ROYAL_GOLD, "owner_only": True, "commands": []},
    "music":   {"label": "🎵  NHẠC",         "color": ROYAL_GOLD, "commands": []},
    "deobf":   {"label": "🔓  GIẢI MÃ",      "color": 0x00FFCC,   "commands": []},
    "obf":     {"label": "🎭  OBFUSCATE",    "color": 0xFF8800,   "commands": []},
    "realtime":{"label": "⚡  REAL-TIME",    "color": ROYAL_GOLD, "commands": []},
    "tools":   {"label": "🛠️  TOOLS",        "color": 0x00D9FF,   "commands": []},
    "fun":     {"label": "🎮  FUN",          "color": 0xFF00FF,   "commands": []},
    "util":    {"label": "⚙️  UTIL",         "color": 0xAAAAAA,   "commands": []},
    "admin":   {"label": "👑  ADMIN",        "color": ROYAL_RED,  "admin_only": True, "commands": []},
}


def _register_help():
    H = HELP_CATS
    H["roast"]["commands"] = [
        ("!chui @user [tier]", "Chửi (nhe|vua|nang|huydiet|mega)"),
        ("!combo @user [số]", "Combo 4-12 câu"),
        ("!megachui @user", "Nổ 3 phát mega"),
        ("!autochui @user [giây]", "Auto chửi"),
        ("!stopchui", "Dừng"),
        ("!roastall", "Chửi 5 người random"),
        ("!setgender @user <nam|nu|neutral>", "Set giới tính"),
        ("!checkgender [@user]", "Check"),
        ("!roastdb / !resetroast", "Stats / Reset"),
        ("!maxpower / !autoconfig", "Config"),
        ("!stats", "Bảng vàng chiến tích"),
    ]
    H["fake"]["commands"] = [
        ("!fake @user [text]", "Fake tin"),
        ("!fake on|off|status|rebuild|name", "Quản lý webhook"),
        ("!fakecombo @user", "Fake 4 tin"),
        ("!autofake @user [giây]", "Auto fake"),
        ("!spam @user [tin] [giây]", "Spam burst"),
        ("!burst @user [số]", "Nổ N tin"),
        ("!stopfake / !stopspam / !stopall", "Dừng"),
        ("!whstatus / !whdebug / !whrebuild", "Pool"),
    ]
    H["spamtin"]["commands"] = [
        ("!spamtin @user <số> <giây> <text>", "Spam custom"),
        ("{i} / {t}", "Số / Tên"),
        ("!stopspamtin", "Dừng"),
    ]
    H["mirror"]["commands"] = [
        ("!mirror on|off|del", "Bật/tắt mirror"),
        ("!mirrorlog [số]", "Xem log"),
        ("!mirrorclear", "Xóa log"),
        ("!restore [số]", "Khôi phục embed"),
        ("!restorewebhook [số]", "Khôi phục webhook"),
    ]
    H["afk"]["commands"] = [
        ("!afk <lý do>", "Set AFK"),
        ("!unafk", "Clear"),
        ("!afkstatus", "Danh sách"),
        ("!afkdel <on|off>", "Xóa tin gốc"),
    ]
    H["autodel"]["commands"] = [
        ("!autodel @user <giây>", "Xoá tin user (0 = ngay)"),
        ("!autodel", "Xem config"),
        ("!autodel off", "Tắt"),
        ("!autodeloff", "Tắt nhanh"),
    ]
    H["voice"]["commands"] = [
        ("!join / !leave", "Vào / rời voice"),
        ("!speak [preset] [Nx] <text>", "TTS"),
        ("!stop", "Dừng"),
        ("Preset", "nam nu namtre tre gia robot quai vutru ngau nguoima embe"),
    ]
    H["voicechat"]["commands"] = [
        ("!voicechat", "Bật (owner)"),
        ("!stopvc / !vcstatus", "Tắt / Status"),
        ("!whispertest", "Test Whisper"),
    ]
    H["music"]["commands"] = [
        ("!player <bài>, <bài>", "Music Player + Lyrics"),
        ("!lyrics <tên bài>", "Xem lyrics"),
        ("!volume [N|Nx]", "Chỉnh âm lượng (0-300%)"),
        ("!play <tên/link>", "Phát nhạc"),
        ("!queue / !skip / !pause", "Điều khiển"),
        ("!stopmusic / !loop / !np", "Khác"),
    ]
    H["deobf"]["commands"] = [("!deobf <text|file|reply>", "Decode")]
    H["obf"]["commands"] = [
        ("!obf <text>", "Local obf"),
        ("!obf -ai <text>", "AI obfuscate"),
    ]
    H["realtime"]["commands"] = [
        ("!thoitiet <tp>", "Thời tiết"),
        ("!crypto [coin]", "Crypto"),
        ("!tygia <số> <từ> <sang>", "Tỷ giá"),
        ("!news [source]", "Tin"),
        ("!wiki <từ khoá>", "Wikipedia"),
        ("!ip <địa chỉ>", "IP info"),
    ]
    H["tools"]["commands"] = [
        ("!download <url> [audio]", "Tải video/audio"),
        ("!mp3 <url>", "Shortcut audio"),
        ("!tiktok <url>", "TikTok no watermark"),
        ("!img2pdf", "Ảnh → PDF"),
        ("!compress [quality]", "Nén ảnh"),
        ("!convert <fmt>", "Đổi định dạng ảnh"),
        ("!resize <WxH>", "Đổi kích thước"),
        ("!exif", "Xem EXIF ảnh"),
        ("!dns <domain>", "Tra DNS"),
        ("!domain <domain>", "Info domain"),
        ("!pinghost <host>", "Ping host (ICMP)"),
        ("!portcheck <host> <port>", "Check port"),
        ("!headers <url>", "HTTP headers"),
        ("!httpcheck <url>", "HTTP status"),
        ("!subnet <CIDR>", "Tính subnet"),
        ("!uuid [số]", "Tạo UUID"),
        ("!password [độ dài]", "Password mạnh"),
        ("!hash <text>", "MD5/SHA"),
        ("!aes <enc|dec> <key> <text>", "AES"),
        ("!paste <text>", "Paste lên hastebin"),
        ("!github <user>", "Info GitHub"),
        ("!speedtest", "Test tốc độ mạng"),
        ("!expand <url>", "Mở rộng short URL"),
    ]
    H["fun"]["commands"] = [
        ("!truth / !dare", "Truth or Dare"),
        ("!never", "Never have I ever"),
        ("!wyr", "Would you rather"),
        ("!pickup", "Thả thính"),
        ("!riddle / !riddleanswer", "Đố vui"),
        ("!joke", "Joke"),
        ("!8ball <câu hỏi>", "Magic 8-ball"),
        ("!coinflip / !roll", "Xu / xúc xắc"),
        ("!poll", "Poll"),
        ("!ship @u1 @u2", "Độ hợp (random 100%)"),
        ("!gamble <bet> <tai|xiu>", "Tài xỉu"),
        ("!quote / !poem", "Quote / thơ"),
        ("!avatar / !banner / !userinfo", "Info user"),
        ("!serverinfo", "Info server"),
        ("!qr / !shorten", "QR / rút gọn"),
        ("!waifu / !husbando", "Anime"),
        ("!rank", "BXH"),
        ("!snipe / !editsnipe", "Snipe"),
        ("!remind / !timer", "Nhắc"),
        ("!philo / !philo5 / !xamvn", "Triết lý"),
        ("!video / !video10", "Video"),
        ("!shorts [kw]", "YT Short"),
    ]
    H["util"]["commands"] = [
        ("!lhelp / !h / !menu", "Menu"),
        ("!purge <số> [@user]", "Xoá tin"),
        ("!check", "Quota API"),
        ("!dbstatus", "Stats DB"),
        ("!auditlog [số]", "Audit log (owner)"),
        ("!testapi / !ping", "Test"),
        ("!clearuser @user", "Xoá memory"),
        ("!checkhelp / !helpdebug", "Debug help"),
    ]
    H["admin"]["commands"] = [
        ("!addadmin / !deladmin / !listadmin", "Admin"),
        ("!adduser / !deluser / !listuser", "User"),
        ("!turnon / !turnoff", "Bật/tắt chat"),
        ("!resetwebhook", "Reset webhook"),
    ]


try:
    _register_help()
    log.info("Help registered — %d cats", len(HELP_CATS))
except Exception as _e:
    log.error("_register_help: %s", _e)


def _help_main_embed(user, is_adm, is_own):
    total = sum(len(c["commands"]) for c in HELP_CATS.values())
    role = "ĐẠI ĐẾ" if is_own else ("CẬN THẦN" if is_adm else "THẦN DÂN")
    e = discord.Embed(
        title=_bv_title(),
        description=(f"⚔️ **Đế vương tọa trấn:** {user.mention}\n"
                     f"🎖️ **Đẳng cấp:** `{role}`\n"
                     f"📜 **Số chiếu chỉ:** `{total}`\n\n"
                     f"### ↳ Quỳ xuống, chọn lệnh bên dưới, khanh\n"
                     f"-# Trẫm cấm cãi, chỉ được tuân theo."),
        color=ROYAL_GOLD)
    if HELP_GIF:
        e.set_image(url=HELP_GIF)
    e.set_footer(text="⚔️ Thiên hạ này là của bố mày — cấm cãi")
    return e


def _help_cat_embed(key):
    cat = HELP_CATS[key]
    if not cat["commands"]:
        try:
            _register_help()
        except Exception:
            pass
    if not cat["commands"]:
        body = "*Chưa có chiến chỉ nào.*"
    else:
        body = "\n".join(f"⚜️ `{cmd}` — *{desc}*" for cmd, desc in cat["commands"])
    e = discord.Embed(title=f"📜  {cat['label']}", description=body[:3900], color=cat["color"])
    e.set_footer(text="↩️ Quay về ngai vàng")
    return e


class HelpView(discord.ui.View):
    def __init__(self, user, is_adm, is_own):
        super().__init__(timeout=300)
        opts = []
        for key, cat in HELP_CATS.items():
            if cat.get("admin_only") and not is_adm:
                continue
            if cat.get("owner_only") and not is_own:
                continue
            opts.append(discord.SelectOption(label=cat["label"][:100], value=key))
        if opts:
            sel = discord.ui.Select(placeholder="Chọn khu vực...",
                                    min_values=1, max_values=1, options=opts[:25], row=0)

            async def cb(interaction):
                if interaction.user.id != user.id:
                    await interaction.response.send_message(
                        "🤬 Đây là menu của trẫm, mày đéo có quyền!",
                        ephemeral=True)
                    return
                k = interaction.data["values"][0]
                await interaction.response.edit_message(embed=_help_cat_embed(k), view=self)
            sel.callback = cb
            self.add_item(sel)
        close = discord.ui.Button(label="Đóng", emoji="✖️",
                                  style=discord.ButtonStyle.danger, row=1)

        async def ccb(interaction):
            if interaction.user.id != user.id:
                return
            try:
                await interaction.message.delete()
            except Exception:
                pass
        close.callback = ccb
        self.add_item(close)


@bot.command(name="lhelp", aliases=["bhelp", "h", "menu"])
async def cmd_help(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    adm = is_admin(ctx.author)
    own = is_owner(ctx.author)
    await ctx.send(embed=_help_main_embed(ctx.author, adm, own),
                   view=HelpView(ctx.author, adm, own))


@bot.command(name="checkhelp")
async def cmd_checkhelp(ctx):
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    real = {c.name for c in bot.commands} | {a for c in bot.commands for a in c.aliases}
    missing = []
    for cat_key, cat in HELP_CATS.items():
        for cmd, _ in cat["commands"]:
            first = cmd.strip().split()[0].lstrip("!").lower()
            if first in ("preset", "voice", "") or first.startswith("{"):
                continue
            if first not in real:
                missing.append(f"{cat_key}: {cmd}")
    if not missing:
        await ctx.reply(_bv_ok_msg("✅ Tất cả chiếu chỉ đều tồn tại. Trẫm đã kiểm duyệt."))
    else:
        await ctx.send(_bv_err_msg(
            "Lệnh ma:\n```\n" + "\n".join(missing[:40]) + "\n```"))


@bot.command(name="helpdebug")
async def cmd_helpdebug(ctx):
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    e = discord.Embed(title="🔍 TRẪM ĐANG KIỂM DUYỆT", color=ROYAL_GOLD)
    total = 0
    for k, v in HELP_CATS.items():
        n = len(v["commands"])
        total += n
        e.add_field(name=k, value=f"`{n}` · {v['label'][:40]}", inline=False)
    e.set_footer(text=f"Tổng: {total} chiếu chỉ")
    await ctx.send(embed=e)


@bot.command(name="purge", aliases=["clear", "xoa", "clearmsg"])
async def cmd_purge(ctx, amount: str = None, member: discord.Member = None):
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.guild:
        return
    if amount is None:
        await ctx.reply("⚔️ `!purge <số> [@user]`")
        return
    try:
        n = int(amount)
    except Exception:
        await ctx.reply(_bv_err_msg("Số đéo phải số."))
        return
    if n < 1 or n > 500:
        await ctx.reply(_bv_err_msg("Chỉ 1-500 thôi."))
        return
    try:
        await ctx.message.delete()
    except Exception:
        pass
    check = (lambda m: m.author.id == member.id) if member else (lambda m: True)
    try:
        deleted = await ctx.channel.purge(limit=n, check=check, bulk=True)
        msg = await ctx.send(_bv_ok_msg(f"⚔️ Trẫm đã xoá `{len(deleted)}` tin rác."))
        await asyncio.sleep(3)
        try:
            await msg.delete()
        except Exception:
            pass
    except Exception as e:
        try:
            await ctx.send(_bv_err_msg(str(e)[:200]))
        except Exception:
            pass


# ============================================================
# HELPERS
# ============================================================
def _fmt_size(n):
    try:
        n = float(n)
    except Exception:
        return "?"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"


def _safe_filename(s):
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(s))
    s = re.sub(r"\s+", " ", s).strip()
    return (s[:80] or "media").strip("._")


def _is_valid_url(u):
    try:
        p = urllib.parse.urlparse(u)
        return p.scheme in ("http", "https") and p.netloc
    except Exception:
        return False


async def _get_bytes_from_url(url, max_size=25 * 1024 * 1024, timeout=60):
    try:
        s = await http()
        async with s.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as r:
            if r.status != 200:
                return None, f"HTTP {r.status}"
            data = await r.read()
            if len(data) > max_size:
                return None, f"Quá lớn ({len(data)/1024/1024:.1f}MB)"
            return data, None
    except asyncio.TimeoutError:
        return None, "timeout"
    except Exception as e:
        return None, str(e)[:200]


async def _get_image_input(msg):
    attachments = list(msg.attachments)
    if not attachments and msg.reference:
        try:
            ref = msg.reference.resolved
            if ref and hasattr(ref, "attachments"):
                attachments = list(ref.attachments)
        except Exception:
            pass
    for att in attachments:
        ct = att.content_type or ""
        if ct.startswith("image/"):
            data, err = await _get_bytes_from_url(att.url)
            if data:
                return data, att.filename or "image", None
            return None, None, err
    return None, None, "Đéo có ảnh nào. Gửi ảnh kèm hoặc reply ảnh."


# ============================================================
# DOWNLOAD
# ============================================================
def _ytdlp_download_sync(url, audio_only=False, max_mb=25):
    if not YTDL_OK:
        return None, "yt-dlp chưa cài"
    tmpdir = tempfile.mkdtemp(prefix="dl_")
    outtmpl = os.path.join(tmpdir, "%(title).80s.%(ext)s")
    opts = {
        "outtmpl": outtmpl, "quiet": True, "no_warnings": True,
        "noplaylist": True, "nocheckcertificate": True,
        "ignoreerrors": False, "socket_timeout": 30, "retries": 3,
        "max_filesize": max_mb * 1024 * 1024,
        "http_headers": {"User-Agent": "Mozilla/5.0"},
    }
    if audio_only:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3", "preferredquality": "192",
        }]
    else:
        opts["format"] = "best[filesize<{}M]/best".format(max_mb)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                return None, "Đéo extract được"
            if "entries" in info and info["entries"]:
                info = info["entries"][0]
            filepath = ydl.prepare_filename(info)
            if audio_only:
                base = os.path.splitext(filepath)[0]
                mp3path = base + ".mp3"
                if os.path.exists(mp3path):
                    filepath = mp3path
            if not os.path.exists(filepath):
                for f in os.listdir(tmpdir):
                    fp = os.path.join(tmpdir, f)
                    if os.path.isfile(fp):
                        filepath = fp
                        break
            if not os.path.exists(filepath):
                return None, "File đéo tồn tại"
            size = os.path.getsize(filepath)
            if size > max_mb * 1024 * 1024:
                return None, f"File {_fmt_size(size)} vượt {max_mb}MB"
            with open(filepath, "rb") as f:
                data = f.read()
            title = info.get("title", "media")
            ext = info.get("ext", "mp4")
            if audio_only:
                ext = "mp3"
            try:
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception:
                pass
            return {
                "data": data,
                "filename": f"{_safe_filename(title)}.{ext}",
                "title": title,
                "duration": info.get("duration", 0) or 0,
                "uploader": info.get("uploader") or info.get("channel") or "?",
                "thumbnail": info.get("thumbnail", ""),
                "size": size, "ext": ext,
            }, None
    except Exception as e:
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass
        return None, str(e)[:300]


@bot.command(name="download", aliases=["dl", "tai", "taive"])
async def cmd_download(ctx, url: str = None, flag: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not YTDL_OK:
        await ctx.reply(_bv_err_msg("yt-dlp đéo có. pip install yt-dlp"))
        return
    if not FFMPEG_BIN:
        await ctx.reply(_bv_err_msg("ffmpeg đéo có."))
        return
    if not url:
        await ctx.reply(
            "⚔️ **TRẪM BAN LỆNH TẢI XUỐNG**\n"
            "`!download <url>` — Video\n"
            "`!download <url> audio` — MP3\n"
            "`!mp3 <url>` — Shortcut audio")
        return
    if not _is_valid_url(url):
        await ctx.reply(_bv_err_msg("URL sai cú pháp."))
        return

    audio_only = bool(flag and flag.lower() in ("audio", "mp3", "-a", "--audio"))

    async with ctx.typing():
        status = await ctx.send(f"{_bv_loading()}\n"
                                 f"-# Tải {'audio' if audio_only else 'video'} từ `{url[:80]}`")
        try:
            result, err = await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(
                    executor, _ytdlp_download_sync, url, audio_only, 25),
                timeout=180)
        except asyncio.TimeoutError:
            try:
                await status.edit(content=_bv_err_msg("Timeout 180s. Mạng như cứt."))
            except Exception:
                pass
            return

        if err or not result:
            try:
                await status.edit(content=_bv_err_msg(err or "Lỗi đéo rõ"))
            except Exception:
                pass
            return

        try:
            await status.delete()
        except Exception:
            pass

        e = discord.Embed(
            title=f"👑 {_bv_ok()}",
            description=f"**{result['title'][:200]}**",
            color=ROYAL_GOLD,
            timestamp=discord.utils.utcnow())
        e.add_field(name="📺 Kênh", value=f"`{result['uploader'][:80]}`", inline=True)
        if result["duration"]:
            e.add_field(name="⏱️ Dài", value=fmt_dur(result["duration"]), inline=True)
        e.add_field(name="💾 Size", value=_fmt_size(result["size"]), inline=True)
        if result.get("thumbnail", "").startswith("http"):
            e.set_thumbnail(url=result["thumbnail"])
        e.set_footer(text=f"Trẫm ban cho {ctx.author.display_name}")

        try:
            await ctx.send(
                embed=e,
                file=discord.File(io.BytesIO(result["data"]),
                                   filename=result["filename"]))
        except discord.HTTPException as he:
            if he.status == 413:
                await ctx.send(_bv_err_msg(
                    f"File {_fmt_size(result['size'])} quá lớn — Discord từ chối"))
            else:
                await ctx.send(_bv_err_msg(f"Discord lỗi: {str(he)[:200]}"))
        except Exception as ex:
            await ctx.send(_bv_err_msg(f"Gửi file lỗi: {str(ex)[:200]}"))


@bot.command(name="mp3", aliases=["audio", "extractaudio"])
async def cmd_mp3(ctx, url: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not url:
        await ctx.reply("⚔️ Dùng: `!mp3 <url>`")
        return
    await cmd_download(ctx, url, "audio")


# ============================================================
# TIKTOK
# ============================================================
async def _tiktok_get(url):
    try:
        s = await http()
        data = {"url": url, "hd": "1"}
        headers = {"User-Agent": "Mozilla/5.0",
                   "Content-Type": "application/x-www-form-urlencoded"}
        async with s.post("https://www.tikwm.com/api/", data=data,
                           headers=headers,
                           timeout=aiohttp.ClientTimeout(total=30)) as r:
            if r.status != 200:
                return None, f"HTTP {r.status}"
            j = await r.json()
            if j.get("code") != 0:
                return None, j.get("msg", "API error")
            d = j.get("data") or {}
            return {
                "title": d.get("title", ""),
                "author": (d.get("author") or {}).get("unique_id", "?"),
                "duration": d.get("duration", 0),
                "cover": d.get("cover", ""),
                "video_url": d.get("play") or d.get("hdplay") or "",
            }, None
    except Exception as e:
        return None, str(e)[:300]


async def _tiktok_fallback(url):
    """✅ Fallback: yt-dlp khi tikwm chết."""
    if not YTDL_OK:
        return None, "yt-dlp chưa cài"
    try:
        loop = asyncio.get_running_loop()

        def _extract():
            opts = {
                "format": "best[filesize<25M]/best",
                "quiet": True, "no_warnings": True,
                "noplaylist": True, "nocheckcertificate": True,
                "http_headers": {"User-Agent": "Mozilla/5.0"},
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        info = await loop.run_in_executor(executor, _extract)
        if not info:
            return None, "yt-dlp không extract được"
        if "entries" in info and info["entries"]:
            info = info["entries"][0]
        video_url = info.get("url")
        if not video_url and info.get("formats"):
            for f in info["formats"]:
                if f.get("vcodec") != "none" and f.get("ext") == "mp4":
                    video_url = f.get("url")
                    if f.get("filesize") and f["filesize"] < 25 * 1024 * 1024:
                        break
        if not video_url:
            return None, "Đéo lấy được link video"
        return {
            "title": info.get("title", "TikTok"),
            "author": info.get("uploader") or info.get("channel") or "?",
            "duration": info.get("duration", 0),
            "cover": info.get("thumbnail", ""),
            "video_url": video_url,
        }, None
    except Exception as e:
        return None, f"yt-dlp: {str(e)[:200]}"


@bot.command(name="tiktok", aliases=["tt", "tiktokdl"])
async def cmd_tiktok(ctx, url: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not url or "tiktok" not in url.lower():
        await ctx.reply(
            "⚔️ **TIKTOK DL**\n"
            "`!tiktok <url>`\n"
            "-# Không watermark, chất lượng gốc.")
        return

    async with ctx.typing():
        status = await ctx.send(_bv_loading())
        info, err = await _tiktok_get(url)
        if err or not info:
            info, err = await _tiktok_fallback(url)
        if err or not info:
            try:
                await status.edit(content=_bv_err_msg(err or "Đéo lấy được info"))
            except Exception:
                pass
            return

        video_url = info.get("video_url", "")
        if not video_url:
            try:
                await status.edit(content=_bv_err_msg("Đéo lấy được link video"))
            except Exception:
                pass
            return

        if video_url.startswith("//"):
            video_url = "https:" + video_url
        elif video_url.startswith("/"):
            video_url = "https://www.tikwm.com" + video_url

        data, err2 = await _get_bytes_from_url(video_url, max_size=25 * 1024 * 1024)
        if err2 or not data:
            try:
                await status.edit(content=_bv_err_msg(err2 or "Đéo tải video"))
            except Exception:
                pass
            return

        try:
            await status.delete()
        except Exception:
            pass

        e = discord.Embed(
            title=f"🎵 {str(info.get('title', 'TikTok'))[:200]}",
            color=0xFE2C55, timestamp=discord.utils.utcnow())
        e.add_field(name="👤 Author",
                    value=f"@{str(info.get('author', '?'))[:50]}", inline=True)
        if info.get("duration"):
            e.add_field(name="⏱️", value=f"{info['duration']}s", inline=True)
        e.add_field(name="💾", value=_fmt_size(len(data)), inline=True)
        if info.get("cover", "").startswith("http"):
            e.set_thumbnail(url=info["cover"])
        e.set_footer(text=f"Trẫm ban cho {ctx.author.display_name}")

        filename = f"tiktok_{int(time.time())}.mp4"
        try:
            await ctx.send(embed=e,
                            file=discord.File(io.BytesIO(data), filename=filename))
        except discord.HTTPException as he:
            if he.status == 413:
                await ctx.send(_bv_err_msg(f"Video {_fmt_size(len(data))} quá lớn"))
            else:
                await ctx.send(_bv_err_msg(str(he)[:200]))


# ============================================================
# IMAGE
# ============================================================
@bot.command(name="img2pdf", aliases=["images2pdf"])
async def cmd_img2pdf(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not PIL_OK:
        await ctx.reply(_bv_err_msg("Pillow đéo có. pip install Pillow"))
        return

    attachments = list(ctx.message.attachments)
    if not attachments and ctx.message.reference:
        try:
            ref = ctx.message.reference.resolved
            if ref and hasattr(ref, "attachments"):
                attachments = list(ref.attachments)
        except Exception:
            pass

    imgs = [a for a in attachments if (a.content_type or "").startswith("image/")]
    if not imgs:
        await ctx.reply("⚔️ Gửi ảnh kèm lệnh, hoặc reply tin có ảnh.")
        return
    if len(imgs) > 20:
        imgs = imgs[:20]

    async with ctx.typing():
        status = await ctx.send(f"{_bv_loading()}\n-# Gom `{len(imgs)}` ảnh thành PDF")
        images_data = []
        for att in imgs:
            data, err = await _get_bytes_from_url(att.url, max_size=15 * 1024 * 1024)
            if data:
                images_data.append(data)

        if not images_data:
            try:
                await status.edit(content=_bv_err_msg("Đéo tải được ảnh nào"))
            except Exception:
                pass
            return

        def _make_pdf():
            try:
                images = []
                for d in images_data:
                    try:
                        img = Image.open(io.BytesIO(d))
                        if img.mode != "RGB":
                            img = img.convert("RGB")
                        images.append(img)
                    except Exception:
                        continue
                if not images:
                    return None
                buf = io.BytesIO()
                images[0].save(buf, format="PDF", save_all=True,
                                append_images=images[1:], quality=85)
                for im in images:
                    try:
                        im.close()
                    except Exception:
                        pass
                return buf.getvalue()
            except Exception:
                return None

        try:
            pdf_bytes = await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(executor, _make_pdf),
                timeout=120)
        except asyncio.TimeoutError:
            try:
                await status.edit(content=_bv_err_msg("Timeout."))
            except Exception:
                pass
            return

        if not pdf_bytes:
            try:
                await status.edit(content=_bv_err_msg("Đéo tạo được PDF"))
            except Exception:
                pass
            return

        try:
            await status.delete()
        except Exception:
            pass

        await ctx.send(
            content=_bv_ok_msg(f"📄 PDF từ `{len(images_data)}` ảnh ({_fmt_size(len(pdf_bytes))})"),
            file=discord.File(io.BytesIO(pdf_bytes),
                               filename=f"images_{int(time.time())}.pdf"))


@bot.command(name="compress", aliases=["cmp"])
async def cmd_compress(ctx, quality: int = 75):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not PIL_OK:
        await ctx.reply(_bv_err_msg("Pillow đéo có."))
        return
    data, fname, err = await _get_image_input(ctx.message)
    if not data:
        await ctx.reply(_bv_err_msg(err))
        return

    quality = max(10, min(95, int(quality)))

    def _do():
        try:
            img = Image.open(io.BytesIO(data))
            if img.mode in ("RGBA", "P", "LA"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            img.close()
            return buf.getvalue()
        except Exception:
            return None

    async with ctx.typing():
        out = await run_blocking(_do, timeout=30)
    if not out:
        await ctx.reply(_bv_err_msg("Nén thất bại"))
        return

    orig_size = len(data)
    new_size = len(out)
    saved = (1 - new_size / orig_size) * 100 if orig_size else 0

    e = discord.Embed(title=f"🗜️ {_bv_ok()}", color=ROYAL_GOLD)
    e.add_field(name="Trước", value=_fmt_size(orig_size), inline=True)
    e.add_field(name="Sau", value=_fmt_size(new_size), inline=True)
    e.add_field(name="Tiết kiệm", value=f"{saved:+.1f}%", inline=True)
    e.add_field(name="Quality", value=f"`{quality}`", inline=True)

    base = os.path.splitext(fname or "image")[0]
    await ctx.send(embed=e, file=discord.File(
        io.BytesIO(out), filename=f"{base}_compressed.jpg"))


@bot.command(name="convert", aliases=["cv", "chuyendinhdang"])
async def cmd_convert(ctx, fmt: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not PIL_OK:
        await ctx.reply(_bv_err_msg("Pillow đéo có."))
        return
    if not fmt:
        await ctx.reply("⚔️ Dùng: `!convert <png|jpg|jpeg|webp|bmp|gif|ico>`")
        return
    fmt = fmt.lower().lstrip(".")
    fmt_map = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG",
               "webp": "WEBP", "bmp": "BMP", "gif": "GIF",
               "ico": "ICO", "tiff": "TIFF"}
    if fmt not in fmt_map:
        await ctx.reply(_bv_err_msg("Format đéo hỗ trợ."))
        return

    data, fname, err = await _get_image_input(ctx.message)
    if not data:
        await ctx.reply(_bv_err_msg(err))
        return

    pil_fmt = fmt_map[fmt]

    def _do():
        try:
            img = Image.open(io.BytesIO(data))
            if pil_fmt == "JPEG" and img.mode in ("RGBA", "P", "LA"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = bg
            elif pil_fmt == "JPEG" and img.mode != "RGB":
                img = img.convert("RGB")
            buf = io.BytesIO()
            save_kwargs = {}
            if pil_fmt == "JPEG":
                save_kwargs["quality"] = 90
            img.save(buf, format=pil_fmt, **save_kwargs)
            img.close()
            return buf.getvalue()
        except Exception:
            return None

    async with ctx.typing():
        out = await run_blocking(_do, timeout=30)
    if not out:
        await ctx.reply(_bv_err_msg("Convert lỗi"))
        return

    base = os.path.splitext(fname or "image")[0]
    await ctx.send(
        content=_bv_ok_msg(f"🔄 {_fmt_size(len(data))} → {_fmt_size(len(out))} · `{fmt}`"),
        file=discord.File(io.BytesIO(out), filename=f"{base}.{fmt}"))


@bot.command(name="resize", aliases=["rs", "doikichthuoc"])
async def cmd_resize(ctx, size: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not PIL_OK:
        await ctx.reply(_bv_err_msg("Pillow đéo có."))
        return
    if not size:
        await ctx.reply("⚔️ `!resize <WxH>` — vd `!resize 800x600`\n"
                         "`!resize 800x` giữ tỷ lệ.")
        return
    m = re.match(r"^(\d+)?x(\d+)?$", size.lower())
    if not m:
        await ctx.reply(_bv_err_msg("Format sai."))
        return
    w = int(m.group(1)) if m.group(1) else None
    h = int(m.group(2)) if m.group(2) else None
    if w is None and h is None:
        await ctx.reply(_bv_err_msg("Cần ít nhất 1 chiều."))
        return
    if w and (w < 1 or w > 8000):
        await ctx.reply(_bv_err_msg("W 1-8000"))
        return
    if h and (h < 1 or h > 8000):
        await ctx.reply(_bv_err_msg("H 1-8000"))
        return

    data, fname, err = await _get_image_input(ctx.message)
    if not data:
        await ctx.reply(_bv_err_msg(err))
        return

    def _do():
        try:
            img = Image.open(io.BytesIO(data))
            ow, oh = img.size
            if w and h:
                nw, nh = w, h
            elif w:
                nw = w
                nh = int(oh * w / ow)
            else:
                nh = h
                nw = int(ow * h / oh)
            img2 = img.resize((nw, nh), Image.LANCZOS)
            buf = io.BytesIO()
            save_fmt = "PNG" if img2.mode in ("RGBA", "P", "LA") else "JPEG"
            img2.save(buf, format=save_fmt, quality=92)
            img.close()
            img2.close()
            return buf.getvalue(), nw, nh, ow, oh, save_fmt
        except Exception:
            return None

    async with ctx.typing():
        res = await run_blocking(_do, timeout=30)
    if not res:
        await ctx.reply(_bv_err_msg("Resize lỗi"))
        return

    out, nw, nh, ow, oh, save_fmt = res
    ext = "png" if save_fmt == "PNG" else "jpg"
    base = os.path.splitext(fname or "image")[0]

    await ctx.send(
        content=_bv_ok_msg(f"📐 {ow}x{oh} → {nw}x{nh}"),
        file=discord.File(io.BytesIO(out), filename=f"{base}_{nw}x{nh}.{ext}"))


@bot.command(name="exif", aliases=["meta", "imgmeta"])
async def cmd_exif(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not PIL_OK:
        await ctx.reply(_bv_err_msg("Pillow đéo có."))
        return
    data, fname, err = await _get_image_input(ctx.message)
    if not data:
        await ctx.reply(_bv_err_msg(err))
        return

    def _do():
        try:
            img = Image.open(io.BytesIO(data))
            info = {"format": img.format or "?", "mode": img.mode, "size": img.size}
            exif_data = {}
            try:
                exif = img.getexif()
                if exif:
                    for k, v in exif.items():
                        tag = str(k)
                        try:
                            from PIL.ExifTags import TAGS
                            tag = TAGS.get(k, str(k))
                        except Exception:
                            pass
                        exif_data[tag] = str(v)[:200]
            except Exception:
                pass
            img.close()
            return info, exif_data
        except Exception:
            return None, None

    async with ctx.typing():
        info, exif_data = await run_blocking(_do, timeout=15) or (None, None)
    if not info:
        await ctx.reply(_bv_err_msg("Đéo đọc được ảnh."))
        return

    e = discord.Embed(title=f"📷 {_bv_ok()}", color=ROYAL_GOLD)
    e.add_field(name="Format", value=f"`{info['format']}`", inline=True)
    e.add_field(name="Mode", value=f"`{info['mode']}`", inline=True)
    e.add_field(name="Size", value=f"`{info['size'][0]}x{info['size'][1]}`", inline=True)

    if exif_data:
        important = ["Make", "Model", "DateTime", "Software", "ExposureTime",
                     "FNumber", "ISOSpeedRatings", "FocalLength", "GPSInfo",
                     "Orientation", "Flash", "WhiteBalance"]
        lines = []
        for key in important:
            if key in exif_data:
                lines.append(f"**{key}**: `{exif_data[key][:80]}`")
        extra = [k for k in exif_data if k not in important][:10]
        for k in extra:
            lines.append(f"`{k}`: `{exif_data[k][:60]}`")
        if lines:
            e.add_field(name=f"EXIF ({len(exif_data)} tags)",
                        value="\n".join(lines)[:1000], inline=False)
    else:
        e.add_field(name="EXIF", value="*Ảnh này đéo có EXIF*", inline=False)

    await ctx.send(embed=e)


# ============================================================
# NETWORK
# ============================================================
@bot.command(name="dns", aliases=["dnslookup", "lookup"])
async def cmd_dns(ctx, domain: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not domain:
        await ctx.reply("⚔️ Dùng: `!dns <domain>`")
        return

    domain = domain.strip().lower()
    domain = re.sub(r"^https?://", "", domain).split("/")[0].split(":")[0]
    if not re.match(r"^[a-zA-Z0-9._\-]+$", domain):
        await ctx.reply(_bv_err_msg("Domain sai cú pháp."))
        return

    e = discord.Embed(title=f"🌐 TRẪM TRA DNS — {domain}",
                      color=ROYAL_GOLD, timestamp=discord.utils.utcnow())

    async def _doh_query(qtype):
        try:
            s = await http()
            url = f"https://dns.google/resolve?name={urllib.parse.quote(domain)}&type={qtype}"
            async with s.get(url, timeout=10,
                             headers={"Accept": "application/dns-json"}) as r:
                if r.status != 200:
                    return []
                data = await r.json()
                answers = data.get("Answer", []) or []
                out = []
                for a in answers:
                    if a.get("data"):
                        out.append(a["data"])
                return list(dict.fromkeys(out))[:10]
        except Exception:
            return []

    try:
        infos = socket.getaddrinfo(domain, None)
        a_recs = sorted({i[4][0] for i in infos if i[0] == socket.AF_INET})
        aaaa_recs = sorted({i[4][0] for i in infos if i[0] == socket.AF_INET6})
    except Exception:
        a_recs = await _doh_query("A")
        aaaa_recs = await _doh_query("AAAA")

    mx_recs = await _doh_query("MX")
    ns_recs = await _doh_query("NS")
    txt_recs = await _doh_query("TXT")
    cname_recs = await _doh_query("CNAME")

    for key, val in (("A", a_recs), ("AAAA", aaaa_recs), ("CNAME", cname_recs),
                     ("MX", mx_recs), ("NS", ns_recs), ("TXT", txt_recs)):
        if val:
            v = "\n".join(f"• `{str(x)[:100]}`" for x in val[:8])
            e.add_field(name=key, value=v[:1000], inline=False)

    if not e.fields:
        e.description = _bv_err_msg("Đéo tra được record nào.")
    else:
        e.description = "**" + _bv_ok() + "**"

    await ctx.send(embed=e)


@bot.command(name="domain", aliases=["domaininfo"])
async def cmd_domain(ctx, domain: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not domain:
        await ctx.reply("⚔️ Dùng: `!domain <domain>`")
        return
    domain = re.sub(r"^https?://", "", domain).strip().lower().split("/")[0].split(":")[0]

    e = discord.Embed(title=f"🔍 TRẪM TRA DOMAIN — {domain}",
                       color=ROYAL_GOLD, timestamp=discord.utils.utcnow())

    try:
        ip = socket.gethostbyname(domain)
        e.add_field(name="📡 A record", value=f"`{ip}`", inline=True)
    except Exception:
        e.add_field(name="📡 A record", value="❌ đéo resolve", inline=True)

    try:
        s = await http()
        async with s.get(f"https://{domain}/",
                         timeout=aiohttp.ClientTimeout(total=10),
                         allow_redirects=True, ssl=False) as r:
            e.add_field(name="🌐 HTTPS", value=f"`{r.status}`", inline=True)
            server = r.headers.get("Server", "?")
            e.add_field(name="🖥️ Server", value=f"`{server[:80]}`", inline=True)
            if r.headers.get("X-Powered-By"):
                e.add_field(name="⚡ X-Powered-By",
                             value=f"`{r.headers['X-Powered-By'][:80]}`", inline=True)
    except Exception:
        try:
            s = await http()
            async with s.get(f"http://{domain}/",
                             timeout=aiohttp.ClientTimeout(total=10),
                             allow_redirects=True, ssl=False) as r:
                e.add_field(name="🌐 HTTP", value=f"`{r.status}`", inline=True)
        except Exception:
            e.add_field(name="🌐 HTTP/HTTPS", value="❌ đéo kết nối", inline=True)

    try:
        s = await http()
        async with s.get(f"https://rdap.org/domain/{domain}",
                         timeout=aiohttp.ClientTimeout(total=15),
                         headers={"User-Agent": "Mozilla/5.0"}) as r:
            if r.status == 200:
                j = await r.json()
                events = {ev.get("eventAction"): ev.get("eventDate", "")
                          for ev in (j.get("events") or [])}
                for k, label in (("registration", "Tạo"),
                                  ("expiration", "Hết hạn"),
                                  ("last changed", "Đổi cuối")):
                    if k in events:
                        e.add_field(name=f"📅 {label}",
                                    value=f"`{events[k][:20]}`", inline=True)
    except Exception:
        pass

    if not e.fields:
        e.description = _bv_err_msg("Đéo lấy được info.")

    await ctx.send(embed=e)


@bot.command(name="pinghost", aliases=["hostping", "icmp"])
async def cmd_pinghost(ctx, host: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not host:
        await ctx.reply("⚔️ Dùng: `!pinghost <host>`")
        return

    host = host.strip().lower()
    host = re.sub(r"^https?://", "", host).split("/")[0].split(":")[0]
    if not re.match(r"^[a-zA-Z0-9._\-]+$", host):
        await ctx.reply(_bv_err_msg("Hostname sai."))
        return

    def _ping():
        if os.name == "nt":
            cmd = ["ping", "-n", "4", host]
        else:
            cmd = ["ping", "-c", "4", "-W", "2", host]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return (r.stdout or "") + (r.stderr or ""), r.returncode
        except subprocess.TimeoutExpired:
            return "", -1
        except Exception as e:
            return str(e), -1

    async with ctx.typing():
        out, rc = await asyncio.wait_for(
            asyncio.get_running_loop().run_in_executor(executor, _ping),
            timeout=20)

    e = discord.Embed(title=f"📡 TRẪM PING — {host}", color=ROYAL_GOLD)

    if rc == -1:
        e.description = _bv_err_msg(f"Timeout: {out[:200]}")
        e.color = ROYAL_RED
    elif rc == 0:
        lines = [l.strip() for l in out.splitlines() if l.strip()][:15]
        summary = "\n".join(f"`{l[:90]}`" for l in lines[-6:])
        e.description = summary or "✅ OK"
        e.color = 0x00FF7F
    else:
        e.description = _bv_err_msg("Đéo ping được. Host chết hoặc block ICMP.")
        e.color = ROYAL_RED

    await ctx.send(embed=e)


@bot.command(name="portcheck", aliases=["pc", "checkport"])
async def cmd_portcheck(ctx, host: str = None, port: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not host or not port:
        await ctx.reply("⚔️ Dùng: `!portcheck <host> <port>`")
        return
    host = re.sub(r"^https?://", "", host).strip().lower().split("/")[0].split(":")[0]
    try:
        port_n = int(port)
        if port_n < 1 or port_n > 65535:
            raise ValueError
    except Exception:
        await ctx.reply(_bv_err_msg("Port 1-65535."))
        return

    def _check():
        try:
            infos = socket.getaddrinfo(host, port_n, type=socket.SOCK_STREAM)
            ip = infos[0][4][0]
        except Exception:
            ip = host
        t0 = time.monotonic()
        try:
            sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sk.settimeout(5.0)
            r = sk.connect_ex((ip, port_n))
            sk.close()
            el = int((time.monotonic() - t0) * 1000)
            return r == 0, ip, el
        except Exception:
            return False, ip, 0

    async with ctx.typing():
        is_open, ip, ms = await asyncio.wait_for(
            asyncio.get_running_loop().run_in_executor(executor, _check),
            timeout=15)

    icon = "🟢" if is_open else "🔴"
    status = "MỞ" if is_open else "ĐÓNG"
    e = discord.Embed(
        title=f"{icon} TRẪM CHECK PORT",
        description=f"**`{host}:{port_n}`** → `{status}`\n"
                    f"IP: `{ip}` · `{ms}ms`",
        color=0x00FF7F if is_open else ROYAL_RED)
    await ctx.send(embed=e)


@bot.command(name="headers", aliases=["hd", "httpheaders"])
async def cmd_headers(ctx, url: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not url:
        await ctx.reply("⚔️ Dùng: `!headers <url>`")
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    async with ctx.typing():
        try:
            s = await http()
            async with s.head(url, timeout=aiohttp.ClientTimeout(total=15),
                              allow_redirects=False, ssl=False) as r:
                headers = dict(r.headers)
                status = r.status
        except Exception as e:
            await ctx.reply(_bv_err_msg(str(e)[:200]))
            return

    e = discord.Embed(title=f"📋 TRẪM XEM HEADERS",
                       description=f"`{url[:100]}`", color=ROYAL_GOLD)
    e.add_field(name="Status", value=f"`{status}`", inline=True)

    lines = []
    for k, v in headers.items():
        lines.append(f"**{k}**: `{str(v)[:120]}`")
    body = "\n".join(lines)[:3900]
    e.add_field(name=f"Headers ({len(headers)})", value=body or "—", inline=False)
    await ctx.send(embed=e)


@bot.command(name="httpcheck", aliases=["hc", "httpstatus"])
async def cmd_httpcheck(ctx, url: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not url:
        await ctx.reply("⚔️ Dùng: `!httpcheck <url>`")
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    async with ctx.typing():
        t0 = time.monotonic()
        try:
            s = await http()
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=20),
                              allow_redirects=True, ssl=False) as r:
                el = int((time.monotonic() - t0) * 1000)
                status = r.status
                final_url = str(r.url)
                redirects = [str(h.url) for h in r.history]
                ct = r.headers.get("Content-Type", "?")
                cl = r.headers.get("Content-Length", "?")
        except Exception as e:
            await ctx.reply(_bv_err_msg(str(e)[:200]))
            return

    icon = "✅" if 200 <= status < 400 else ("⚠️" if status < 500 else "❌")
    e = discord.Embed(title=f"{icon} TRẪM CHECK HTTP", color=ROYAL_GOLD)
    e.add_field(name="Status", value=f"`{status}`", inline=True)
    e.add_field(name="Latency", value=f"`{el}ms`", inline=True)
    e.add_field(name="Redirects", value=f"`{len(redirects)}`", inline=True)
    e.add_field(name="Final URL", value=f"`{final_url[:200]}`", inline=False)
    if ct != "?":
        e.add_field(name="Content-Type", value=f"`{ct[:100]}`", inline=True)
    if cl != "?":
        try:
            e.add_field(name="Size", value=f"`{_fmt_size(int(cl))}`", inline=True)
        except Exception:
            pass
    if redirects:
        e.add_field(name="Chain",
                     value="\n".join(f"→ `{r[:100]}`" for r in redirects[:5])[:1000],
                     inline=False)
    await ctx.send(embed=e)


@bot.command(name="subnet", aliases=["sn", "subnetcalc"])
async def cmd_subnet(ctx, cidr: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not IPADDR_OK:
        await ctx.reply(_bv_err_msg("ipaddress module đéo có."))
        return
    if not cidr:
        await ctx.reply("⚔️ Dùng: `!subnet <CIDR>`\nVD: `!subnet 192.168.1.0/24`")
        return

    try:
        net = ipaddress.ip_network(cidr, strict=False)
    except Exception as e:
        await ctx.reply(_bv_err_msg(str(e)[:200]))
        return

    e = discord.Embed(title=f"🌐 TRẪM TÍNH SUBNET — {cidr}", color=ROYAL_GOLD)
    e.add_field(name="Network", value=f"`{net.network_address}`", inline=True)
    e.add_field(name="Broadcast", value=f"`{net.broadcast_address}`", inline=True)
    e.add_field(name="Netmask", value=f"`{net.netmask}`", inline=True)
    e.add_field(name="Wildcard", value=f"`{net.hostmask}`", inline=True)
    e.add_field(name="Prefix", value=f"`/{net.prefixlen}`", inline=True)
    e.add_field(name="Version", value=f"`IPv{net.version}`", inline=True)
    try:
        e.add_field(name="Hosts", value=f"`{net.num_addresses - 2:,}`", inline=True)
        e.add_field(name="Total IPs", value=f"`{net.num_addresses:,}`", inline=True)
    except Exception:
        pass

    if net.num_addresses <= 65536:
        try:
            hosts = list(net.hosts())
            if hosts:
                e.add_field(name="Range",
                             value=f"`{hosts[0]}` → `{hosts[-1]}`", inline=False)
        except Exception:
            pass

    if net.version == 4:
        e.add_field(name="Private?",
                     value=f"`{'YES' if net.is_private else 'NO'}`", inline=True)
        e.add_field(name="Global?",
                     value=f"`{'YES' if net.is_global else 'NO'}`", inline=True)

    await ctx.send(embed=e)


log.info("tools.py v9.4 BLOCK 1/2 — Help + Download + Image + Network loaded")
# tools.py v9.4 — BLOCK 2/2
# Crypto + Util + Fun + Autodel + Tasks + Events + start_bot()
# ✅ FIX v9.4: Multi-fallback cho mọi API, autodel dùng *, args

# ============================================================
# CRYPTO
# ============================================================
@bot.command(name="uuid", aliases=["guid"])
async def cmd_uuid(ctx, count: int = 1):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    import uuid as _uuid
    count = max(1, min(20, count))
    uuids = [str(_uuid.uuid4()) for _ in range(count)]
    if count == 1:
        await ctx.reply(_bv_ok_msg(f"🎲 `{uuids[0]}`"))
    else:
        body = "\n".join(f"`{i+1}.` `{u}`" for i, u in enumerate(uuids))
        await ctx.send(_bv_ok_msg(f"🎲 **{count} UUIDs:**\n{body[:1900]}"))


@bot.command(name="password", aliases=["pw", "genpass", "matkhau"])
async def cmd_password(ctx, length: int = 16, *flags):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    length = max(6, min(128, length))

    use_symbol = use_num = use_upper = use_lower = True
    fl = " ".join(flags).lower()
    if "--no-symbol" in fl or "-ns" in fl:
        use_symbol = False
    if "--no-num" in fl or "-nn" in fl:
        use_num = False
    if "--no-upper" in fl or "-nu" in fl:
        use_upper = False
    if "--no-lower" in fl or "-nl" in fl:
        use_lower = False

    pool = ""
    if use_lower:
        pool += "abcdefghijklmnopqrstuvwxyz"
    if use_upper:
        pool += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if use_num:
        pool += "0123456789"
    if use_symbol:
        pool += "!@#$%^&*()-_=+[]{};:,.<>?"

    if not pool:
        await ctx.reply(_bv_err_msg("Bật ít nhất 1 loại ký tự."))
        return

    pwd = "".join(random.choice(pool) for _ in range(length))

    strength = 0
    if length >= 12:
        strength += 1
    if length >= 16:
        strength += 1
    if use_lower and use_upper:
        strength += 1
    if use_num:
        strength += 1
    if use_symbol:
        strength += 1

    labels = ["💀 Yếu", "🔴 Yếu", "🟡 TB", "🟢 Khá", "🔵 Mạnh", "🟣 Cực mạnh"]
    label = labels[min(strength, len(labels) - 1)]

    try:
        import math
        entropy = round(length * math.log2(len(pool)), 1)
    except Exception:
        entropy = 0

    e = discord.Embed(title=f"🔐 {_bv_ok()}", color=ROYAL_GOLD)
    e.add_field(name="Password", value=f"||`{pwd}`||", inline=False)
    e.add_field(name="Độ dài", value=f"`{length}`", inline=True)
    e.add_field(name="Độ mạnh", value=label, inline=True)
    e.add_field(name="Entropy", value=f"`{entropy} bits`", inline=True)
    e.set_footer(text="Click spoiler để xem · Tự xoá sau 5 phút")
    msg = await ctx.send(embed=e)

    async def _del():
        await asyncio.sleep(300)
        try:
            await msg.delete()
        except Exception:
            pass
    asyncio.create_task(_del())


@bot.command(name="hash", aliases=["bam", "mahoa"])
async def cmd_hash(ctx, *, text: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not text:
        await ctx.reply("⚔️ Dùng: `!hash <text>`")
        return

    data = text.encode("utf-8")
    md5 = hashlib.md5(data).hexdigest()
    sha1 = hashlib.sha1(data).hexdigest()
    sha256 = hashlib.sha256(data).hexdigest()
    sha512 = hashlib.sha512(data).hexdigest()

    e = discord.Embed(title=f"🔐 {_bv_ok()}",
                       description=f"Input: `{text[:200]}`", color=ROYAL_GOLD)
    e.add_field(name="MD5", value=f"`{md5}`", inline=False)
    e.add_field(name="SHA1", value=f"`{sha1}`", inline=False)
    e.add_field(name="SHA256", value=f"`{sha256}`", inline=False)
    e.add_field(name="SHA512", value=f"`{sha512[:128]}...`", inline=False)
    e.set_footer(text=f"Length: {len(data)} bytes")
    await ctx.send(embed=e)


@bot.command(name="aes", aliases=["aesenc"])
async def cmd_aes(ctx, mode: str = None, key: str = None, *, text: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not mode or not key or not text:
        await ctx.reply(
            "⚔️ **TRẪM BAN LỆNH AES**\n"
            "`!aes enc <key> <text>` — Mã hoá\n"
            "`!aes dec <key> <base64>` — Giải mã")
        return

    mode = mode.lower()
    is_enc = mode in ("enc", "encrypt", "ma", "mã")
    is_dec = mode in ("dec", "decrypt", "giai", "giải")
    if not (is_enc or is_dec):
        await ctx.reply(_bv_err_msg("Mode: `enc` hoặc `dec`"))
        return

    def _do_aes():
        try:
            from hashlib import sha256 as _sha256
            k = _sha256(key.encode("utf-8")).digest()
            iv = b"\x00" * 16
            try:
                from Crypto.Cipher import AES
                from Crypto.Util.Padding import pad, unpad
                cipher = AES.new(k, AES.MODE_CBC, iv)
                if is_enc:
                    ct = cipher.encrypt(pad(text.encode("utf-8"), 16))
                    return base64.b64encode(ct).decode(), None
                else:
                    raw = base64.b64decode(text)
                    pt = unpad(cipher.decrypt(raw), 16)
                    return pt.decode("utf-8"), None
            except ImportError:
                if is_enc:
                    data = text.encode("utf-8")
                    out = bytes(b ^ k[i % len(k)] for i, b in enumerate(data))
                    return base64.b64encode(out).decode(), "⚠️ Fallback XOR — cài pycryptodome"
                else:
                    data = base64.b64decode(text)
                    out = bytes(b ^ k[i % len(k)] for i, b in enumerate(data))
                    return out.decode("utf-8"), "⚠️ Fallback XOR"
        except Exception as e:
            return None, str(e)[:200]

    result, err = await run_blocking(_do_aes, timeout=15)

    if err and result is None:
        await ctx.reply(_bv_err_msg(err))
        return

    if is_enc:
        e = discord.Embed(title=f"🔒 {_bv_ok()}", color=0x00FF7F)
        e.add_field(name="Key", value=f"`{key[:40]}`", inline=True)
        e.add_field(name="Mode",
                     value="`AES-CBC`" if "Fallback" not in (err or "") else "`XOR`",
                     inline=True)
        e.add_field(name="Encrypted", value=f"```\n{result}\n```", inline=False)
        if err:
            e.set_footer(text=err)
        await ctx.send(embed=e)
    else:
        e = discord.Embed(title=f"🔓 {_bv_ok()}", color=ROYAL_GOLD)
        e.add_field(name="Key", value=f"`{key[:40]}`", inline=True)
        e.add_field(name="Decrypted", value=f"```\n{result[:1900]}\n```", inline=False)
        if err:
            e.set_footer(text=err)
        await ctx.send(embed=e)


# ============================================================
# UTIL
# ============================================================
@bot.command(name="paste", aliases=["pastebin", "haste"])
async def cmd_paste(ctx, *, text: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return

    content = ""
    if text:
        content = text
    elif ctx.message.attachments:
        att = ctx.message.attachments[0]
        data, err = await _get_bytes_from_url(att.url, max_size=5 * 1024 * 1024)
        if data:
            try:
                content = data.decode("utf-8")
            except Exception:
                content = data.decode("latin-1", errors="ignore")
    elif ctx.message.reference:
        try:
            ref = ctx.message.reference.resolved
            if ref and ref.content:
                content = ref.content
        except Exception:
            pass

    if not content or len(content.strip()) < 3:
        await ctx.reply("⚔️ Dùng: `!paste <text>` hoặc gửi file / reply tin.")
        return

    if len(content) > 500000:
        await ctx.reply(_bv_err_msg(f"Text dài {len(content):,} ký tự > 500k"))
        return

    async with ctx.typing():
        url = None
        source = "?"

        # ✅ Primary: paste.rs
        try:
            s = await http()
            async with s.post("https://paste.rs/",
                              data=content.encode("utf-8"),
                              timeout=aiohttp.ClientTimeout(total=30),
                              headers={"User-Agent": "Mozilla/5.0",
                                       "Content-Type": "text/plain"}) as r:
                if r.status in (200, 201):
                    txt = (await r.text()).strip()
                    if txt.startswith("http"):
                        url = txt
                        source = "paste.rs"
        except Exception:
            pass

        # ✅ Fallback: 0x0.st
        if not url:
            try:
                s = await http()
                form = aiohttp.FormData()
                form.add_field("file", content.encode("utf-8"),
                               filename="paste.txt", content_type="text/plain")
                form.add_field("expires", "72")
                async with s.post("https://0x0.st",
                                  data=form,
                                  timeout=aiohttp.ClientTimeout(total=30),
                                  headers={"User-Agent": "Mozilla/5.0"}) as r:
                    if r.status == 200:
                        txt = (await r.text()).strip()
                        if txt.startswith("http"):
                            url = txt
                            source = "0x0.st"
            except Exception:
                pass

        # ✅ Fallback 2: hastebin.com
        if not url:
            try:
                s = await http()
                async with s.post("https://hastebin.com/documents",
                                  data=content.encode("utf-8"),
                                  timeout=aiohttp.ClientTimeout(total=30),
                                  headers={"User-Agent": "Mozilla/5.0"}) as r:
                    if r.status in (200, 201):
                        j = await r.json()
                        key = j.get("key")
                        if key:
                            url = f"https://hastebin.com/{key}"
                            source = "hastebin"
            except Exception:
                pass

        if not url:
            await ctx.reply(_bv_err_msg("Cả paste.rs, 0x0.st, hastebin đều fail."))
            return

        e = discord.Embed(
            title=f"📋 {_bv_ok()}",
            description=f"[Xem tại đây]({url})",
            color=ROYAL_GOLD)
        e.add_field(name="Nguồn", value=f"`{source}`", inline=True)
        e.add_field(name="Size", value=f"`{len(content):,}` ký tự", inline=True)
        e.add_field(name="Lines",
                    value=f"`{content.count(chr(10)) + 1:,}`", inline=True)
        e.set_footer(text=f"Trẫm ban cho {ctx.author.display_name}")
        await ctx.send(embed=e)


@bot.command(name="github", aliases=["gh"])
async def cmd_github(ctx, username: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not username:
        await ctx.reply("⚔️ Dùng: `!github <username>`")
        return
    username = username.strip().lstrip("@")

    async with ctx.typing():
        try:
            s = await http()
            async with s.get(f"https://api.github.com/users/{username}",
                             timeout=aiohttp.ClientTimeout(total=15),
                             headers={"User-Agent": "Mozilla/5.0",
                                      "Accept": "application/vnd.github+json"}) as r:
                if r.status == 404:
                    await ctx.reply(_bv_err_msg(f"Đéo có user `{username}`"))
                    return
                if r.status != 200:
                    await ctx.reply(_bv_err_msg(f"GitHub API: HTTP {r.status}"))
                    return
                j = await r.json()
        except Exception as e:
            await ctx.reply(_bv_err_msg(str(e)[:200]))
            return

    name = j.get("name") or j.get("login", "?")
    bio = j.get("bio") or "*Đéo có bio*"
    location = j.get("location") or "?"
    company = j.get("company") or "?"
    blog = j.get("blog") or ""
    followers = j.get("followers", 0)
    following = j.get("following", 0)
    repos = j.get("public_repos", 0)
    gists = j.get("public_gists", 0)
    created = j.get("created_at", "")[:10]
    avatar = j.get("avatar_url", "")
    url = j.get("html_url", "")

    e = discord.Embed(
        title=f"👤 TRẪM TRA GITHUB — {name}",
        url=url,
        description=bio[:500],
        color=0x24292F)
    if avatar:
        e.set_thumbnail(url=avatar)
    e.add_field(name="📛 Username", value=f"`{j.get('login', '?')}`", inline=True)
    e.add_field(name="📍 Địa điểm", value=f"`{location[:50]}`", inline=True)
    e.add_field(name="🏢 Company", value=f"`{company[:50]}`", inline=True)
    e.add_field(name="👥 Followers", value=f"`{followers:,}`", inline=True)
    e.add_field(name="👣 Following", value=f"`{following:,}`", inline=True)
    e.add_field(name="📦 Public repos", value=f"`{repos:,}`", inline=True)
    e.add_field(name="📝 Gists", value=f"`{gists:,}`", inline=True)
    e.add_field(name="📅 Tham gia", value=f"`{created}`", inline=True)
    if blog:
        e.add_field(name="🔗 Website", value=blog[:100], inline=False)
    e.set_footer(text="GitHub API · 60 req/h")
    await ctx.send(embed=e)


@bot.command(name="speedtest", aliases=["stest", "netspeed"])
async def cmd_speedtest(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not is_owner(ctx.author):
        await ctx.reply(_bv_err_msg("Chỉ trẫm dùng được. Tốn băng thông lắm."))
        return

    st = await ctx.send(f"{_bv_loading()}\n-# Test tốc độ mạng (10-60s)")

    def _do():
        try:
            import speedtest as _st
            s = _st.Speedtest()
            s.get_best_server()
            dl = s.download() / 1_000_000
            ul = s.upload() / 1_000_000
            ping = s.results.ping
            server = s.results.server
            return {
                "download": round(dl, 2),
                "upload": round(ul, 2),
                "ping": round(ping, 1),
                "server": f"{server.get('name', '?')} ({server.get('country', '?')})",
                "isp": s.results.client.get("isp", "?"),
            }, None
        except ImportError:
            return None, "speedtest-cli đéo có. pip install speedtest-cli"
        except Exception as e:
            return None, str(e)[:200]

    result, err = await run_blocking(_do, timeout=90)

    if err:
        try:
            await st.edit(content=_bv_err_msg(err))
        except Exception:
            pass
        return

    e = discord.Embed(title=f"⚡ {_bv_ok()}", color=ROYAL_GOLD)
    e.add_field(name="📥 Download", value=f"`{result['download']:,} Mbps`", inline=True)
    e.add_field(name="📤 Upload", value=f"`{result['upload']:,} Mbps`", inline=True)
    e.add_field(name="📡 Ping", value=f"`{result['ping']} ms`", inline=True)
    e.add_field(name="🏢 Server", value=f"`{result['server'][:80]}`", inline=False)
    e.add_field(name="🌐 ISP", value=f"`{result['isp'][:80]}`", inline=True)
    e.set_footer(text="speedtest.net")
    try:
        await st.edit(content=None, embed=e)
    except Exception:
        await ctx.send(embed=e)


@bot.command(name="expand", aliases=["unshort", "murl"])
async def cmd_expand(ctx, url: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not url:
        await ctx.reply("⚔️ Dùng: `!expand <short_url>`")
        return
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    async with ctx.typing():
        try:
            s = await http()
            async with s.head(url, timeout=aiohttp.ClientTimeout(total=15),
                              allow_redirects=False, ssl=False) as r:
                status = r.status
                loc = r.headers.get("Location", "")
                if not loc and 200 <= status < 300:
                    await ctx.reply(_bv_ok_msg("URL này đéo phải short link."))
                    return
                if not loc:
                    await ctx.reply(_bv_err_msg(f"Đéo có Location (HTTP {status})"))
                    return
                chain = [url]
                current = loc
                for _ in range(10):
                    if current.startswith("/"):
                        p = urllib.parse.urlparse(chain[-1])
                        current = f"{p.scheme}://{p.netloc}{current}"
                    if current in chain:
                        break
                    chain.append(current)
                    try:
                        async with s.head(current,
                                          timeout=aiohttp.ClientTimeout(total=10),
                                          allow_redirects=False, ssl=False) as r2:
                            if r2.status in (301, 302, 303, 307, 308):
                                nxt = r2.headers.get("Location", "")
                                if not nxt:
                                    break
                                current = nxt
                            else:
                                break
                    except Exception:
                        break
        except Exception as e:
            await ctx.reply(_bv_err_msg(str(e)[:200]))
            return

    e = discord.Embed(title=f"🔗 {_bv_ok()}", color=ROYAL_GOLD)
    e.add_field(name="Short URL", value=f"`{url[:200]}`", inline=False)
    e.add_field(name="URL gốc", value=f"`{chain[-1][:200]}`", inline=False)
    if len(chain) > 2:
        chain_txt = "\n".join(f"{i+1}. `{c[:100]}`" for i, c in enumerate(chain[:8]))
        e.add_field(name=f"Chain ({len(chain)} bước)",
                     value=chain_txt[:1000], inline=False)
    await ctx.send(embed=e)


# ============================================================
# FUN
# ============================================================
_TRUTH_Q = ["Bí mật lớn nhất của bạn?", "Người bạn thầm thích trong server?",
            "Lần cuối bạn khóc vì ai?", "Điều xấu hổ nhất bạn từng làm?",
            "Bạn từng nói dối bố mẹ chưa?", "Nếu xoá 1 ký ức, bạn xoá gì?",
            "Điều bạn giấu kín nhất với gia đình?", "Bạn đã từng bị bắt quả tang?",
            "Điều bạn hối hận nhất trong đời?", "Người bạn ghét nhất trong server?",
            "Bạn từng thích ai trong server này chưa?",
            "Lần cuối bạn tự sướng là khi nào?",
            "Điều dơ bẩn nhất bạn từng làm mà đéo ai biết?",
            "Bạn từng bị phát hiện nói xấu sau lưng chưa?"]
_DARE_Q = ["Gửi 1 câu chửi bản thân.", "Đổi avatar thành ảnh mèo 1h.",
           "Tag 1 người khen 3 câu.", "Hát 1 câu trong voice.",
           "Gõ `!chui @bản_thân`.", "Kể 1 bí mật chưa ai biết.",
           "Nhắn tin cho crush: 'thích em/anh'.", "Gọi tên 3 người bạn ghét.",
           "Kể về mối tình đầu.", "Nhại giọng 1 thành viên.",
           "Chụp màn hình tin nhắn cuối với crush.",
           "Nói thật 100% điều bạn nghĩ về người ngồi cạnh."]


@bot.command(name="truth")
async def cmd_truth(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    await ctx.reply(_bv_ok_msg(f"🎭 **TRUTH:** {random.choice(_TRUTH_Q)}"))


@bot.command(name="dare")
async def cmd_dare(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    await ctx.reply(_bv_ok_msg(f"🔥 **DARE:** {random.choice(_DARE_Q)}"))


_NEVER_Q = ["uống rượu", "hút thuốc", "đi bar", "nói dối bố mẹ",
            "xem phim 18+", "thức trắng đêm chơi game", "khóc vì phim",
            "yêu đơn phương", "bị đá", "đá người khác",
            "ăn trộm tiền bố mẹ", "trốn học", "quay cóp",
            "nói xấu sau lưng bạn", "phản bội bạn thân",
            "thích người trong server này", "gửi ảnh nóng",
            "say xỉn rồi gọi điện cho crush"]


@bot.command(name="never", aliases=["neverever"])
async def cmd_never(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    await ctx.reply(_bv_ok_msg(f"🍻 Never have I ever — {random.choice(_NEVER_Q)}"))


_WYR = [("có 10 tỷ nhưng độc thân", "có người yêu nhưng nghèo"),
        ("thông minh nhưng xấu", "đẹp nhưng ngu"),
        ("du lịch vòng quanh thế giới", "mua nhà Sài Gòn"),
        ("sống 100 tuổi cô đơn", "sống 40 tuổi hạnh phúc"),
        ("biết trước tương lai", "quay ngược quá khứ"),
        ("mất trí nhớ", "mất mạng sống"),
        ("có 100 tỷ nhưng không được ăn", "nghèo nhưng ăn cả đời"),
        ("đẹp trai/xinh gái nhưng dốt", "xấu nhưng giỏi")]


@bot.command(name="wyr", aliases=["wouldyourather"])
async def cmd_wyr(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    a, b = random.choice(_WYR)
    await ctx.reply(_bv_ok_msg(f"🤔 **Would you rather**\n\n**A)** {a}\n**B)** {b}"))


_PICKUP = [
    "Em có bật lửa không? Anh đang cháy vì em 🔥",
    "Em có phải Google? Em là thứ anh tìm cả đời 🔍",
    "Em có phải wifi? Anh kết nối ngay từ lần đầu 📶",
    "Em có phải cà phê? Đậm đà và làm anh mất ngủ ☕",
    "Em có bản đồ không? Anh bị lạc trong mắt em 🗺️",
    "Em có phải mặt trời? Em làm anh chói mắt ☀️",
    "Em có phải trộm? Em lấy trộm tim anh 💗",
    "Em có phải bác sĩ? Em làm tim anh đập nhanh 💓",
    "Em có phải cầu vồng? Vì em làm anh thấy màu sắc 🌈",
]


@bot.command(name="pickup", aliases=["thaithinh", "flirt"])
async def cmd_pickup(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    await ctx.reply(_bv_ok_msg(f"💘 {random.choice(_PICKUP)}"))


_RIDDLES = [("Cái gì càng rửa càng bẩn?", "nước"),
            ("Cái gì có răng mà không cắn?", "lược"),
            ("Cái gì càng to càng nhẹ?", "cái lỗ"),
            ("Cái gì đi khắp thế giới mà không ra khỏi góc?", "con tem"),
            ("Cái gì có chân mà không đi?", "cái ghế"),
            ("Cái gì có mắt mà không thấy?", "cây kim"),
            ("Cái gì càng lấy càng nhiều?", "ảnh chụp"),
            ("Cái gì mất đầu vẫn sống?", "con giun"),
            ("Cái gì càng đói càng no?", "cái bụng rỗng"),
            ("Cái gì đi nằm mà đứng dậy?", "con rắn")]
_RIDDLE_ANS = {}


@bot.command(name="riddle", aliases=["do", "dovui"])
async def cmd_riddle(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    q, a = random.choice(_RIDDLES)
    await ctx.send(_bv_ok_msg(f"🧩 **Đố:** {q}\n-# Gõ `!riddleanswer` để xem"))
    _RIDDLE_ANS[ctx.channel.id] = (q, a)


@bot.command(name="riddleanswer", aliases=["da"])
async def cmd_riddleanswer(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    entry = _RIDDLE_ANS.get(ctx.channel.id)
    if not entry:
        await ctx.reply(_bv_err_msg("Chưa có đố nào."))
        return
    q, a = entry
    await ctx.reply(_bv_ok_msg(f"📖 **{q}**\n→ **{a}**"))


_JOKES = ["Một con vịt đi qua cầu, cầu sập. Vì vịt quá nặng.",
          "Tại sao máy tính bị ốm? Vì bị virus.",
          "Con gì càng to càng nhỏ? Con cua.",
          "Cái gì đi 1000 dặm mà không mỏi? Con tem.",
          "Tại sao mặt trời không đi học? Vì nó đã sáng rồi.",
          "Con gì càng bơi càng khô? Con cá khô.",
          "Cái gì càng rửa càng dơ? Nước rửa chén bẩn."]


@bot.command(name="joke", aliases=["jokes", "daovui"])
async def cmd_joke(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    await ctx.reply(_bv_ok_msg(f"😂 {random.choice(_JOKES)}"))


_8BALL = ["Có chứ.", "Không đâu.", "Chắc chắn rồi.", "Đéo.",
          "Hỏi lại sau.", "Bố nghĩ là có.", "Đừng mơ.",
          "Có thể.", "Không bao giờ.", "Chuẩn luôn.",
          "Có đấy, nhưng đéo phải với mày.", "Trời biết.",
          "Tự mày biết đi.", "Đúng cmnr."]


@bot.command(name="8ball")
async def cmd_8ball(ctx, *, q: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not q:
        await ctx.reply("⚔️ Dùng: `!8ball <câu hỏi>`")
        return
    await ctx.reply(_bv_ok_msg(f"🎱 *{q}*\n→ **{random.choice(_8BALL)}**"))


@bot.command(name="coinflip", aliases=["cf"])
async def cmd_coinflip(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    await ctx.reply(_bv_ok_msg(f"🪙 **{random.choice(['Sấp', 'Ngửa'])}**"))


@bot.command(name="roll")
async def cmd_roll(ctx, dice: str = "1d6"):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    m = re.match(r"^(\d+)d(\d+)$", dice.lower())
    if not m:
        await ctx.reply(_bv_err_msg("Dùng: `!roll 2d6`"))
        return
    n, s = int(m.group(1)), int(m.group(2))
    if n > 20 or s > 1000:
        await ctx.reply(_bv_err_msg("n≤20, s≤1000."))
        return
    rolls = [random.randint(1, s) for _ in range(n)]
    await ctx.reply(_bv_ok_msg(f"🎲 **{dice}**: {rolls} → **{sum(rolls)}**"))


@bot.command(name="poll", aliases=["binhchon"])
async def cmd_poll(ctx, *, args: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not args or "|" not in args:
        await ctx.reply("⚔️ `!poll <câu> | <opt1> | <opt2>`")
        return
    parts = [x.strip() for x in args.split("|") if x.strip()]
    if len(parts) < 2:
        await ctx.reply(_bv_err_msg("Cần câu hỏi + ít nhất 1 lựa chọn."))
        return
    q, opts = parts[0], parts[1:11]
    emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    lines = [f"**{q}**\n"] + [f"{emojis[i]} {o}" for i, o in enumerate(opts)]
    msg = await ctx.send(_bv_ok_msg("\n".join(lines)))
    for i in range(len(opts)):
        try:
            await msg.add_reaction(emojis[i])
        except Exception:
            pass


@bot.command(name="ship")
async def cmd_ship(ctx, u1: discord.Member = None, u2: discord.Member = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not u1:
        await ctx.reply("⚔️ Dùng: `!ship @u1 [@u2]`")
        return
    u2 = u2 or ctx.author

    pct = random.randint(0, 100)
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)

    if pct >= 95:
        verdict = "💍 Cưới luôn đi, đẹp đôi vcl!"
    elif pct >= 85:
        verdict = "❤️ Đẹp đôi! Tri kỷ đây rồi"
    elif pct >= 70:
        verdict = "😍 Hợp nhau đấy, tiến tới đi"
    elif pct >= 55:
        verdict = "😊 Ổn đấy, thử hẹn hò xem"
    elif pct >= 40:
        verdict = "😐 Tạm được, cần cố gắng thêm"
    elif pct >= 25:
        verdict = "😬 Khó đấy, suy nghĩ lại đi"
    elif pct >= 10:
        verdict = "💔 Thôi bỏ đi, đéo hợp đâu"
    else:
        verdict = "☠️ Thảm họa! Tránh xa nhau ra"

    emoji = random.choice(["💕", "💘", "💖", "💗", "💓", "❤️‍🔥", "😍", "🥰"])

    await ctx.reply(_bv_ok_msg(
        f"{emoji} **{u1.display_name}** × **{u2.display_name}**\n"
        f"`{bar}` **{pct}%**\n{verdict}"))


@bot.command(name="gamble", aliases=["taixiu"])
async def cmd_gamble(ctx, bet: str = None, choice: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not bet or not choice:
        await ctx.reply("⚔️ `!gamble <số> <tai|xiu>`")
        return
    try:
        b = int(bet)
    except Exception:
        await ctx.reply(_bv_err_msg("Số đéo phải số."))
        return
    if b < 1 or b > 10000:
        await ctx.reply(_bv_err_msg("Cược 1-10000."))
        return
    ch = choice.lower()
    if ch not in ("tai", "xiu", "tài", "xỉu"):
        await ctx.reply(_bv_err_msg("Chọn `tai` hoặc `xiu`."))
        return
    d1, d2, d3 = (random.randint(1, 6) for _ in range(3))
    total = d1 + d2 + d3
    result = "tai" if total >= 11 else "xiu"
    win = (ch.startswith("t") and result == "tai") or \
          (ch.startswith("x") and result == "xiu")
    await ctx.reply(_bv_ok_msg(
        f"🎲 {d1}+{d2}+{d3}=**{total}** → **{result.upper()}**\n"
        f"{'✅ Thắng' if win else '❌ Thua'} `{b:,}`"))


_QUOTES = ["Sống là để chết. Chết là để được sống.",
           "Đời người như giấc mộng, tỉnh dậy vẫn nghèo.",
           "Không có gì là mãi mãi, kể cả nỗi đau.",
           "Ai rồi cũng khác, chỉ có tiền là vẫn thế.",
           "Cười người hôm trước, hôm sau người cười.",
           "Đời là bể khổ, nhưng đéo ai bơi được.",
           "Tiền không mua được hạnh phúc. Nhưng thiếu tiền thì cũng đéo."]


@bot.command(name="quote")
async def cmd_quote(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    await ctx.reply(_bv_ok_msg(f'💬 *"{random.choice(_QUOTES)}"*'))


@bot.command(name="poem", aliases=["tho"])
async def cmd_poem(ctx, *, topic: str = "đời"):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    t = topic[:50]
    lines = [f"Bố ngồi ngẫm nghĩ về {t},",
             "Lòng dạ bồi hồi khóe mắt cay.",
             f"Phàm trần ai hiểu thấu {t},",
             "Chỉ có bố đây, bậc đế vương."]
    await ctx.send(_bv_ok_msg("📜 **Thơ:**\n" + "\n".join(lines)))


@bot.command(name="avatar", aliases=["avt"])
async def cmd_avatar(ctx, member: discord.Member = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    m = member or ctx.author
    e = discord.Embed(title=f"🖼️ Avatar của {m.display_name}", color=ROYAL_GOLD)
    e.set_image(url=m.display_avatar.url)
    await ctx.send(embed=e)


@bot.command(name="banner")
async def cmd_banner(ctx, member: discord.Member = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    m = member or ctx.author
    try:
        u = await bot.fetch_user(m.id)
        if not u.banner:
            await ctx.reply(_bv_err_msg("Thằng này đéo có banner."))
            return
        e = discord.Embed(title=f"🎨 Banner của {m.display_name}", color=ROYAL_GOLD)
        e.set_image(url=u.banner.url)
        await ctx.send(embed=e)
    except Exception as ex:
        await ctx.reply(_bv_err_msg(str(ex)[:150]))


@bot.command(name="userinfo", aliases=["whois"])
async def cmd_userinfo(ctx, member: discord.Member = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    m = member or ctx.author
    e = discord.Embed(title=f"👤 Hồ sơ của {m}", color=ROYAL_GOLD)
    e.set_thumbnail(url=m.display_avatar.url)
    e.add_field(name="ID", value=f"`{m.id}`", inline=True)
    e.add_field(name="Bot?", value="có" if m.bot else "không", inline=True)
    e.add_field(name="Tạo",
                 value=m.created_at.strftime("%Y-%m-%d"), inline=True)
    if getattr(m, "joined_at", None):
        e.add_field(name="Vào",
                     value=m.joined_at.strftime("%Y-%m-%d"), inline=True)
    roles = [r.mention for r in getattr(m, "roles", []) if r.name != "@everyone"][:10]
    if roles:
        e.add_field(name="Roles", value=" ".join(roles), inline=False)
    await ctx.send(embed=e)


@bot.command(name="serverinfo", aliases=["guildinfo"])
async def cmd_serverinfo(ctx):
    if not ctx.guild:
        return
    g = ctx.guild
    e = discord.Embed(title=f"🏰 Lãnh thổ {g.name}", color=ROYAL_GOLD)
    if g.icon:
        e.set_thumbnail(url=g.icon.url)
    e.add_field(name="ID", value=f"`{g.id}`", inline=True)
    e.add_field(name="Chủ", value=f"<@{g.owner_id}>", inline=True)
    e.add_field(name="Thần dân", value=f"{g.member_count:,}", inline=True)
    e.add_field(name="Kênh", value=str(len(g.channels)), inline=True)
    e.add_field(name="Chức", value=str(len(g.roles)), inline=True)
    await ctx.send(embed=e)


@bot.command(name="qr")
async def cmd_qr(ctx, *, text: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not text:
        await ctx.reply("⚔️ Dùng: `!qr <nội dung>`")
        return
    url = (f"https://api.qrserver.com/v1/create-qr-code/"
           f"?size=400x400&data={urllib.parse.quote(text)}")
    e = discord.Embed(title=f"📱 QR — {_bv_ok()}", color=ROYAL_GOLD)
    e.set_image(url=url)
    await ctx.send(embed=e)


@bot.command(name="shorten", aliases=["shorturl"])
async def cmd_shorten(ctx, url: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not url or not url.startswith("http"):
        await ctx.reply("⚔️ Dùng: `!shorten <url>`")
        return

    s = await http()
    short = None
    source = "?"

    # ✅ Primary: tinyurl
    try:
        async with s.get(
            f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(url)}",
            timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 200:
                txt = (await r.text()).strip()
                if txt.startswith("http"):
                    short = txt
                    source = "tinyurl"
    except Exception:
        pass

    # ✅ Fallback: is.gd
    if not short:
        try:
            async with s.get(
                f"https://is.gd/create.php?format=simple&url={urllib.parse.quote(url)}",
                timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    txt = (await r.text()).strip()
                    if txt.startswith("http"):
                        short = txt
                        source = "is.gd"
        except Exception:
            pass

    # ✅ Fallback 2: v.gd
    if not short:
        try:
            async with s.get(
                f"https://v.gd/create.php?format=simple&url={urllib.parse.quote(url)}",
                timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    txt = (await r.text()).strip()
                    if txt.startswith("http"):
                        short = txt
                        source = "v.gd"
        except Exception:
            pass

    if not short:
        await ctx.reply(_bv_err_msg("Cả 3 dịch vụ shorten đều fail."))
        return

    e = discord.Embed(title=f"🔗 {_bv_ok()}", color=ROYAL_GOLD)
    e.add_field(name="Short URL", value=short, inline=False)
    e.add_field(name="Gốc", value=f"`{url[:180]}`", inline=False)
    e.add_field(name="Nguồn", value=f"`{source}`", inline=True)
    await ctx.send(embed=e)


@bot.command(name="waifu")
async def cmd_waifu(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return

    s = await http()
    img = None

    try:
        async with s.get("https://api.waifu.pics/sfw/waifu",
                         timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 200:
                d = await r.json()
                img = d.get("url", "")
    except Exception:
        pass

    if not img:
        try:
            async with s.get("https://nekos.best/api/v2/neko",
                             timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    d = await r.json()
                    results = d.get("results", [])
                    if results:
                        img = results[0].get("url", "")
        except Exception:
            pass

    if not img:
        await ctx.reply(_bv_err_msg("Đéo lấy được ảnh. API chết."))
        return

    e = discord.Embed(title=f"👰 {_bv_ok()}", color=ROYAL_GOLD)
    e.set_image(url=img)
    await ctx.send(embed=e)


@bot.command(name="husbando")
async def cmd_husbando(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return

    s = await http()
    img = None

    try:
        async with s.get("https://api.waifu.pics/sfw/husbando",
                         timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 200:
                d = await r.json()
                img = d.get("url", "")
    except Exception:
        pass

    if not img:
        try:
            async with s.get("https://nekos.best/api/v2/husbando",
                             timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    d = await r.json()
                    results = d.get("results", [])
                    if results:
                        img = results[0].get("url", "")
        except Exception:
            pass

    if not img:
        await ctx.reply(_bv_err_msg("Đéo lấy được ảnh. API chết."))
        return

    e = discord.Embed(title=f"🤴 {_bv_ok()}", color=ROYAL_GOLD)
    e.set_image(url=img)
    await ctx.send(embed=e)


_snipe_cache = {}
_esnipe_cache = {}


@bot.command(name="snipe")
async def cmd_snipe(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    lst = _snipe_cache.get(ctx.channel.id, [])
    if not lst:
        await ctx.reply(_bv_err_msg("Đéo có gì để snipe."))
        return
    name, content, ts = lst[-1]
    e = discord.Embed(title=f"🔫 Snipe — {name}",
                      description=content[:1900] or "*[trống]*",
                      color=ROYAL_RED,
                      timestamp=datetime.fromtimestamp(ts))
    await ctx.send(embed=e)


@bot.command(name="editsnipe", aliases=["esnipe"])
async def cmd_esnipe(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    lst = _esnipe_cache.get(ctx.channel.id, [])
    if not lst:
        await ctx.reply(_bv_err_msg("Đéo có gì."))
        return
    name, before, after, ts = lst[-1]
    e = discord.Embed(title=f"✏️ Edit Snipe — {name}",
                      color=ROYAL_RED,
                      timestamp=datetime.fromtimestamp(ts))
    e.add_field(name="Trước", value=(before[:900] or "—"), inline=False)
    e.add_field(name="Sau", value=(after[:900] or "—"), inline=False)
    await ctx.send(embed=e)


@bot.command(name="remind", aliases=["nhac"])
async def cmd_remind(ctx, duration: str = None, *, text: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not duration or not text:
        await ctx.reply("⚔️ `!remind 10m <nội dung>`")
        return
    sec = _parse_duration(duration)
    if not sec or sec < 5 or sec > 86400:
        await ctx.reply(_bv_err_msg("5s - 24h."))
        return
    channel_id = ctx.channel.id
    author_mention = ctx.author.mention
    await ctx.reply(_bv_ok_msg(f"⏰ Trẫm sẽ nhắc {author_mention} sau `{duration}`."))

    async def _do():
        await asyncio.sleep(sec)
        try:
            ch = bot.get_channel(channel_id)
            if ch:
                await ch.send(f"⏰ **TRẪM NHẮC {author_mention}:** {text}")
        except Exception:
            pass
    asyncio.create_task(_do())


@bot.command(name="timer")
async def cmd_timer(ctx, duration: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not duration:
        await ctx.reply("⚔️ `!timer 5m`")
        return
    sec = _parse_duration(duration)
    if not sec or sec < 1 or sec > 3600:
        await ctx.reply(_bv_err_msg("1s - 1h."))
        return
    mention = ctx.author.mention
    await ctx.reply(f"{_bv_loading()}\n-# Đếm `{duration}`")
    await asyncio.sleep(sec)
    try:
        await ctx.send(f"🔔 **HẾT GIỜ** — {mention}")
    except Exception:
        pass


@bot.command(name="rank", aliases=["bxh"])
async def cmd_rank(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return

    def q():
        return db_run("SELECT user_id, LENGTH(messages) AS sz FROM history "
                      "WHERE channel_id=? ORDER BY sz DESC LIMIT 10",
                      (ctx.channel.id,), many=True) or []
    rows = await asyncio.get_running_loop().run_in_executor(None, q)
    if not rows:
        await ctx.reply(_bv_err_msg("Chưa có ai chat."))
        return
    e = discord.Embed(title="🏆 BẢNG VÀNG THẦN DÂN", color=ROYAL_GOLD)
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (uid, sz) in enumerate(rows):
        try:
            u = await bot.fetch_user(int(uid))
            name = u.display_name
        except Exception:
            name = f"ID:{uid}"
        icon = medals[i] if i < 3 else f"`#{i+1}`"
        lines.append(f"{icon} **{name}** — {sz:,} bytes")
    e.description = "\n".join(lines)
    await ctx.send(embed=e)


_PHILO_DB = [
    "Đạo đức là thứ người có tiền viết ra để người không tiền tuân theo.",
    "Luật pháp sinh ra để bảo vệ kẻ mạnh khỏi kẻ yếu.",
    "Cái gọi là 'truyền thống' chỉ là tập quán của người đã chết.",
    "Tiền không mua được hạnh phúc, nhưng nó mua được sự im lặng của nỗi đau.",
    "Kẻ trộm 10 triệu bị tù 10 năm. Kẻ trộm 10 tỷ được gọi là doanh nhân.",
    "Người ta sợ chết vì chưa sống đủ. Sợ sống vì đã chết bên trong.",
    "Cuộc đời không có câu trả lời, chỉ có lựa chọn.",
    "Người thông minh biết mình không biết gì.",
    "Quyền lực không tha hóa con người. Nó bộc lộ bản chất thật.",
    "Lịch sử được viết bởi kẻ chiến thắng.",
    "Cái chết không đáng sợ. Đáng sợ là chết mà không biết mình đã từng sống.",
    "Yêu thương là thứ duy nhất cho đi mà không mất gì.",
    "Chăm chỉ không được thưởng. Kết quả mới được thưởng.",
    "Thành công không đến từ may mắn. Nhưng may mắn là yếu tố 50%.",
]
_PHILO_AUTHORS = ["Mr. AI", "Kẻ quan sát", "Người đứng ngoài",
                  "Máy móc vô tình", "Kẻ không ngủ", "Bộ não không tim",
                  "Anonymous"]


def _cap(s):
    return (s[0].upper() + s[1:]) if s else s


@bot.command(name="philo", aliases=["trietly", "xam"])
async def cmd_philo(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    e = discord.Embed(color=0x1A1A1A)
    e.description = (f'*"{_cap(random.choice(_PHILO_DB))}"*\n\n'
                     f'— **{random.choice(_PHILO_AUTHORS)}**')
    await ctx.send(embed=e)


@bot.command(name="philo5", aliases=["trietly5"])
async def cmd_philo5(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    samples = random.sample(_PHILO_DB, min(5, len(_PHILO_DB)))
    lines = [f'*"{_cap(q)}"*\n— **{random.choice(_PHILO_AUTHORS)}**'
             for q in samples]
    e = discord.Embed(title="🧠  TRIẾT LÝ",
                      description="\n\n".join(lines), color=0x1A1A1A)
    await ctx.send(embed=e)


@bot.command(name="xamvn")
async def cmd_xamvn(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    quotes = [
        "Không có tiền thì đừng nói đạo lý. Có tiền rồi thì đéo cần nói.",
        "Tiền không mua được hạnh phúc. Nhưng thiếu tiền thì cũng đéo hạnh phúc được.",
        "Yêu nhau không chỉ vì tiền, mà vì rất nhiều tiền.",
        "Học nhiều không bằng sống lâu. Sống lâu không bằng gặp thời.",
    ]
    e = discord.Embed(color=0x1A1A1A)
    e.description = f'*"{random.choice(quotes)}"*\n\n— **Ông bà ta**'
    await ctx.send(embed=e)


_YT_QUERIES = ["funny shorts viral", "hai huoc viet nam", "funny cats",
                "funny fails", "vietnamese comedy", "hài hoài linh",
                "try not to laugh", "meme compilation"]
_REDDIT_SUBS = ["funnyvideos", "ContagiousLaughter", "instant_regret",
                "Unexpected", "WatchPeopleDieInside", "HolUp"]
_VIDEO_CACHE = {}
_VIDEO_CACHE_TTL = 600
_VIDEO_LOCK = __import__("threading").Lock()


def _video_cache_get(key):
    with _VIDEO_LOCK:
        ent = _VIDEO_CACHE.get(key)
        if ent and time.time() - ent["t"] < _VIDEO_CACHE_TTL:
            return ent["v"]
        if ent:
            _VIDEO_CACHE.pop(key, None)
    return None


def _video_cache_set(key, v):
    with _VIDEO_LOCK:
        _VIDEO_CACHE[key] = {"t": time.time(), "v": v}


_YDL_FAST_OPTS = {
    "quiet": True, "no_warnings": True, "noplaylist": True,
    "nocheckcertificate": True, "ignoreerrors": True,
    "extract_flat": "in_playlist", "skip_download": True,
    "default_search": "ytsearch5:", "socket_timeout": 10,
    "geo_bypass": True, "http_headers": {"User-Agent": "Mozilla/5.0"},
    "cachedir": False,
}
_ydl_fast = yt_dlp.YoutubeDL(_YDL_FAST_OPTS) if YTDL_OK else None


def _yt_fast_search(query):
    if not _ydl_fast:
        return None
    ck = f"yt:{query}"
    cached = _video_cache_get(ck)
    if cached:
        return cached
    try:
        data = _ydl_fast.extract_info(f"ytsearch5:{query}", download=False)
        if not data or "entries" not in data:
            return None
        entries = [e for e in data["entries"] if e and e.get("id")]
        if not entries:
            return None
        v = random.choice(entries)
        vid_id = v.get("id", "")
        if not vid_id:
            return None
        out = {"title": v.get("title", "?"),
               "url": v.get("url") or f"https://youtu.be/{vid_id}",
               "duration": v.get("duration", 0) or 0,
               "thumbnail": f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg",
               "channel": v.get("uploader") or v.get("channel") or "?",
               "views": v.get("view_count", 0) or 0,
               "platform": "YouTube"}
        _video_cache_set(ck, out)
        return out
    except Exception:
        return None


async def _reddit_video_fast():
    s = await http()
    for _ in range(2):
        sub = random.choice(_REDDIT_SUBS)
        try:
            async with s.get(
                f"https://www.reddit.com/r/{sub}/hot.json?limit=20",
                timeout=aiohttp.ClientTimeout(total=8),
                headers={"User-Agent": "Mozilla/5.0 (bot)"}) as r:
                if r.status != 200:
                    continue
                data = await r.json()
                vids = []
                for p in data.get("data", {}).get("children", []):
                    d = p.get("data", {})
                    if d.get("is_video") and d.get("media"):
                        vids.append({
                            "title": d.get("title", "?")[:200],
                            "url": f"https://reddit.com{d.get('permalink', '')}",
                            "duration": d["media"].get("reddit_video", {}).get("duration", 0),
                            "thumbnail": d.get("thumbnail", ""),
                            "channel": f"r/{d.get('subreddit', '?')}",
                            "views": d.get("score", 0),
                            "platform": "Reddit"})
                if vids:
                    return random.choice(vids)
        except Exception:
            continue
    return None


@bot.command(name="video", aliases=["vid"])
async def cmd_video(ctx, *, keyword: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not YTDL_OK:
        await ctx.reply(_bv_err_msg("yt-dlp đéo có."))
        return
    async with ctx.typing():
        coros = []
        if random.random() < 0.6:
            coros.append(_reddit_video_fast())
        q = keyword.strip() if keyword else random.choice(_YT_QUERIES)
        coros.append(run_blocking(_yt_fast_search, q, timeout=15))
        results = await asyncio.gather(*coros, return_exceptions=True)
        v = None
        for r in results:
            if isinstance(r, dict) and r.get("url"):
                v = r
                break
        if not v:
            await ctx.reply(_bv_err_msg("Đéo tìm được video nào."))
            return
        e = discord.Embed(title=f"🎬 {v['title'][:200]}",
                          url=v["url"], color=ROYAL_GOLD)
        if v.get("thumbnail", "").startswith("http"):
            e.set_image(url=v["thumbnail"])
        e.add_field(name="📺", value=f"`{v['channel'][:80]}`", inline=True)
        if v.get("duration"):
            e.add_field(name="⏱️", value=fmt_dur(v["duration"]), inline=True)
        e.add_field(name="🌐", value=f"`{v.get('platform', '?')}`", inline=True)
        await ctx.send(embed=e)


@bot.command(name="video10", aliases=["vid10"])
async def cmd_video10(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not YTDL_OK:
        await ctx.reply(_bv_err_msg("yt-dlp đéo có."))
        return
    async with ctx.typing():
        tasks = [run_blocking(_yt_fast_search, random.choice(_YT_QUERIES),
                              timeout=15) for _ in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        vids = [r for r in results if isinstance(r, dict)]
        if not vids:
            await ctx.reply(_bv_err_msg("Đéo tìm được video."))
            return
        for v in vids:
            e = discord.Embed(title=f"🎬 {v['title'][:200]}",
                              url=v["url"], color=ROYAL_GOLD)
            if v.get("thumbnail", "").startswith("http"):
                e.set_image(url=v["thumbnail"])
            e.set_footer(text=f"🌐 {v.get('platform', '?')} · {v['channel'][:60]}")
            try:
                await ctx.send(embed=e)
                await asyncio.sleep(0.7)
            except Exception:
                continue


@bot.command(name="shorts", aliases=["yt"])
async def cmd_shorts(ctx, *, keyword: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not YTDL_OK:
        await ctx.reply(_bv_err_msg("yt-dlp đéo có."))
        return
    async with ctx.typing():
        v = await run_blocking(_yt_fast_search,
                                keyword or "funny shorts viral", timeout=15)
        if v and (not v.get("duration") or v["duration"] <= 180):
            e = discord.Embed(title=f"🎬 {v['title'][:200]}",
                              url=v["url"], color=ROYAL_GOLD)
            if v.get("thumbnail"):
                e.set_image(url=v["thumbnail"])
            await ctx.send(embed=e)
        else:
            await ctx.reply(_bv_err_msg("Đéo tìm được short."))


# ============================================================
# AUTO-DELETE
# ============================================================
def _autodel_load(cid):
    try:
        row = db_run("SELECT target_id, seconds, enabled FROM autodel_config WHERE channel_id=?",
                     (cid,), one=True)
        if row:
            return {"target_id": int(row[0] or 0),
                    "seconds": float(row[1] or 0),
                    "enabled": bool(row[2])}
    except Exception:
        pass
    return {"target_id": 0, "seconds": 0.0, "enabled": False}


def _autodel_save(cid, target_id, seconds, enabled):
    try:
        db_run("INSERT OR REPLACE INTO autodel_config(channel_id, target_id, seconds, enabled) "
               "VALUES(?,?,?,?)",
               (cid, int(target_id), float(seconds), 1 if enabled else 0))
    except Exception:
        pass


# ✅ FIX v9.4: dùng *, args để !autodel off không bị parse Member
@bot.command(name="autodel", aliases=["ad", "tuxoa", "autoxoa"])
async def cmd_autodel(ctx, *, args: str = None):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return

    cid = ctx.channel.id

    # ===== KHÔNG CÓ ARGS → XEM CONFIG =====
    if not args or not args.strip():
        cfg = _autodel_load(cid)
        if not cfg["enabled"] or not cfg["target_id"]:
            await ctx.reply(
                "⚔️ **AUTO-DEL** — chưa bật.\n"
                "`!autodel @user <giây>` — Bật\n"
                "• `<giây> = 0` → xoá ngay lập tức\n"
                "• `!autodel off` → tắt")
            return
        sec = cfg["seconds"]
        e = discord.Embed(title="🗑️  AUTO-DEL CONFIG", color=ROYAL_GOLD)
        e.add_field(name="Mục tiêu", value=f"<@{cfg['target_id']}>", inline=True)
        e.add_field(name="Xoá sau",
                    value=f"`{sec:.1f}s`" if sec > 0 else "`NGAY`", inline=True)
        e.add_field(name="Trạng thái", value="🔥 ON", inline=True)
        e.add_field(name="Tắt", value="`!autodel off`", inline=False)
        await ctx.send(embed=e)
        return

    args = args.strip()
    first = args.split(None, 1)[0].lower()

    # ===== !autodel off =====
    if first in ("off", "tat", "tắt", "stop", "0", "disable"):
        _autodel_save(cid, 0, 0, False)
        await ctx.reply(_bv_ok_msg("💤 Đã TẮT auto-delete."))
        return

    # ===== !autodel @user [giây] =====
    m = re.match(r"^<@!?(\d+)>\s*(.*)$", args, re.DOTALL)
    if not m:
        await ctx.reply(_bv_err_msg(
            "Cú pháp sai.\n"
            "`!autodel @user <giây>` — Bật\n"
            "`!autodel off` — Tắt"))
        return

    uid = int(m.group(1))
    sec_str = (m.group(2) or "").strip()

    member = ctx.guild.get_member(uid)
    if not member:
        try:
            member = await ctx.guild.fetch_member(uid)
        except Exception:
            await ctx.reply(_bv_err_msg("Không tìm thấy user."))
            return

    if not sec_str:
        await ctx.reply(_bv_err_msg("Thiếu số giây. VD: `!autodel @user 5`"))
        return

    try:
        sec = float(sec_str.replace(",", ".").rstrip("s"))
    except Exception:
        await ctx.reply(_bv_err_msg("Số giây sai."))
        return

    if sec < 0 or sec > 3600:
        await ctx.reply(_bv_err_msg("Giây từ 0 - 3600."))
        return

    if member.bot:
        await ctx.reply(_bv_err_msg("Đéo xoá bot."))
        return
    if member.id == bot.user.id:
        await ctx.reply(_bv_err_msg("Đéo xoá chính trẫm."))
        return
    if is_owner(member) or is_admin(member):
        await ctx.reply(_bv_err_msg("⚠️ Đây là admin/owner. Đéo xoá."))
        return

    _autodel_save(cid, member.id, sec, True)
    if sec == 0:
        await ctx.reply(_bv_ok_msg(
            f"🗑️ BẬT auto-del — tin của <@{member.id}> bị xoá **NGAY LẬP TỨC**."))
    else:
        await ctx.reply(_bv_ok_msg(
            f"🗑️ BẬT auto-del — tin của <@{member.id}> sẽ bị xoá sau `{sec:.1f}s`."))


@bot.command(name="autodeloff", aliases=["adoff", "stopautodel"])
async def cmd_autodeloff(ctx):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    _autodel_save(ctx.channel.id, 0, 0, False)
    await ctx.reply(_bv_ok_msg("💤 Đã TẮT auto-delete."))


@bot.listen("on_message")
async def _autodel_listener(msg):
    if not msg.guild:
        return
    if msg.content.startswith("!"):
        return
    cid = msg.channel.id
    cfg = _autodel_load(cid)
    if not cfg["enabled"] or not cfg["target_id"]:
        return
    if msg.author.id != cfg["target_id"]:
        return
    try:
        if is_admin(msg.author) or is_owner(msg.author):
            return
    except Exception:
        pass
    sec = cfg["seconds"]
    if sec <= 0:
        try:
            await msg.delete()
        except (discord.NotFound, discord.Forbidden):
            pass
        except Exception as e:
            log.debug("autodel instant: %s", e)
        return
    message_id = msg.id

    async def _del_later(ch_id, m_id, delay):
        try:
            await asyncio.sleep(delay)
            ch = bot.get_channel(ch_id)
            if not ch:
                return
            m = await ch.fetch_message(m_id)
            await m.delete()
        except (discord.NotFound, discord.Forbidden):
            pass
        except Exception:
            pass
    try:
        asyncio.create_task(_del_later(cid, message_id, sec))
    except Exception:
        pass


# ============================================================
# TASKS
# ============================================================
@tasks.loop(hours=1)
async def remind_task():
    if REMIND:
        try:
            ch = bot.get_channel(int(REMIND))
            if ch:
                await ch.send("⏰ Tới giờ")
        except Exception:
            pass


@tasks.loop(minutes=15)
async def cleanup_task():
    now = time.time()
    dead = []
    for k, v in list(_locks.items()):
        if now - v.get("created", now) > 1800:
            dead.append(k)
            continue
        if not v["lock"].locked() and now - v["last"] > 300:
            dead.append(k)
    for k in dead:
        _locks.pop(k, None)


@tasks.loop(minutes=1)
async def voice_task():
    for c in bot.voice_clients:
        try:
            if c.is_connected() and len(c.channel.voice_states) - 1 == 0:
                await c.disconnect()
        except Exception:
            pass


@tasks.loop(minutes=10)
async def health_task():
    try:
        if GEMINI_KEYS:
            alive = sum(1 for i in range(len(GEMINI_KEYS)) if not _is_pen(i, gpen))
            log.info("Gemini: %d/%d", alive, len(GEMINI_KEYS))
        if GROQ_KEYS:
            alive = sum(1 for i in range(len(GROQ_KEYS)) if not _is_pen(i, qpen))
            log.info("Groq: %d/%d", alive, len(GROQ_KEYS))
    except Exception:
        pass


# ============================================================
# EVENTS
# ============================================================
@bot.event
async def on_ready():
    log.info("Bot ready: %s", bot.user)
    log.info("BÁ VƯƠNG ĐẠI ĐẾ v9.4 online (TOOLS BÁ VƯƠNG)")

    # ===== 1. INIT DB + CACHE =====
    for fn, name in ((init_db, "init_db"), (load_admins, "load_admins"),
                     (load_users, "load_users"),
                     (load_custom_roasts, "load_custom_roasts"),
                     (_register_help, "_register_help")):
        try:
            fn()
        except NameError as e:
            log.error("%s chưa define: %s", name, e)
        except Exception as e:
            log.error("%s lỗi: %s", name, e)

    # ===== 2. PRESENCE =====
    try:
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(type=discord.ActivityType.listening, name="!lhelp"))
    except Exception:
        pass

    # ===== 3. START TASKS =====
    for tname in ("remind_task", "cleanup_task", "voice_task", "health_task",
                  "pool_cleanup_task", "flush_counters_task"):
        t = globals().get(tname)
        if t is None:
            log.warning("[TASK] %s chưa define — bỏ qua", tname)
            continue
        try:
            if not t.is_running():
                t.start()
                log.info("[TASK] %s started", tname)
        except Exception as e:
            log.error("[TASK] %s start fail: %s", tname, e)

    # ===== 4. RESTORE WEBHOOK POOL =====
    for guild in bot.guilds:
        for ch in guild.channels:
            if isinstance(ch, (discord.TextChannel, discord.Thread)):
                try:
                    pool = await _wh_restore(ch)
                    if pool:
                        _wh_pool[ch.id] = pool
                except Exception:
                    pass

    # ===== 5. LOAD WHISPER =====
    if VOICE_RECV_OK:
        try:
            asyncio.get_running_loop().run_in_executor(executor, _load_whisper)
        except Exception:
            pass

    # ===== 6. SLASH SYNC =====
    try:
        import os as _os_slash
        _gid_raw = (_os_slash.getenv("GUILD_ID") or "").strip()
        _gid = int(_gid_raw) if _gid_raw.isdigit() else None

        if "sync_slash" in globals():
            try:
                await sync_slash(_gid)
            except TypeError:
                await sync_slash()
            log.info("[SLASH] Sync xong (guild=%s)", _gid or "GLOBAL")
        else:
            log.warning("[SLASH] sync_slash chưa load — check PARTS có slash.py không")
    except Exception as e:
        import traceback
        log.error("[SLASH] sync fail: %s", e)
        traceback.print_exc()

    log.info("Tools Bá Vương ready")


@bot.event
async def on_guild_remove(guild):
    gid = guild.id
    for d, k in [(_roast_tasks, gid), (_fake_tasks, gid),
                 (_fake_tasks, f"spam_{gid}"), (_spamtin_tasks, gid)]:
        t = d.pop(k, None)
        if t and hasattr(t, "cancel") and not t.done():
            t.cancel()
    _auto_roast_targets.pop(gid, None)
    _fake_targets.pop(gid, None)
    _spam_targets.pop(gid, None)
    _voice_history.pop(gid, None)
    for cid in [c.id for c in guild.channels]:
        _wh_pool.pop(cid, None)
        _wh_last_send.pop(cid, None)


@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.content:
        return
    _snipe_cache.setdefault(message.channel.id, []).append(
        (message.author.display_name, message.content, time.time()))
    _snipe_cache[message.channel.id] = _snipe_cache[message.channel.id][-10:]


@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
    _esnipe_cache.setdefault(before.channel.id, []).append(
        (before.author.display_name, before.content, after.content, time.time()))
    _esnipe_cache[before.channel.id] = _esnipe_cache[before.channel.id][-10:]


def _is_bot_mentioned_or_replied(msg):
    if bot.user in msg.mentions:
        return True
    if msg.reference:
        try:
            ref = msg.reference
            if ref.resolved and isinstance(ref.resolved, discord.Message):
                if ref.resolved.author.id == bot.user.id:
                    return True
        except Exception:
            pass
    return False


_swear_cooldown = {}
_SWEAR_CD = 30


@bot.event
async def on_message(msg):
    if msg.author == bot.user or msg.author.bot:
        return
    if not is_allowed(msg.author):
        return
    if msg.content.startswith("!"):
        await bot.process_commands(msg)
        return
    c = msg.content.strip()
    if c.isdigit() and msg.guild:
        try:
            st = mstate(msg.guild.id)
            if st.get("current") and st.get("loop_max", 0) > 0:
                n = int(c)
                if 0 <= n <= 50:
                    st["loop_count"] = 0
                    st["loop_max"] = n
                    await msg.reply(f"🔁 Loop {n}." if n else "🚫 Tắt loop.",
                                    mention_author=False)
                    return
        except Exception:
            pass

    is_dm = isinstance(msg.channel, discord.DMChannel)
    cid = msg.channel.id
    content = msg.content.strip()

    if not is_owner(msg.author) and not msg.webhook_id and content and contains_swear(content):
        if is_dm or (await get_channel_active(cid) != 0):
            _now = time.time()
            _last = _swear_cooldown.get(msg.author.id, 0)
            if _now - _last >= _SWEAR_CD:
                _swear_cooldown[msg.author.id] = _now
                if len(_swear_cooldown) > 5000:
                    _swear_cooldown.clear()
                try:
                    g = detect_gender(msg.author)
                    roast = forge_roast(f"<@{msg.author.id}>",
                                         tier="huydiet",
                                         gender=g, inject_zw=True)
                    if _is_human_on(cid):
                        await reply_as_human(msg, roast)
                    else:
                        await msg.reply(roast, mention_author=False)
                    return
                except Exception as e:
                    log.error("swear back: %s", e)

    hit = _is_bot_mentioned_or_replied(msg)
    if is_dm:
        hit = True
    if not hit:
        return
    if bot.user in msg.mentions:
        content = re.sub(rf"<@!?{bot.user.id}>\s*", "", content).strip()
    if not content:
        try:
            await msg.reply("Gõ `!lhelp`", mention_author=False)
        except Exception:
            pass
        return
    if not is_dm and await get_channel_active(cid) == 0:
        return
    if is_prompt_injection(content):
        try:
            await msg.reply("⚔️ Trẫm đéo tiếp.", mention_author=False)
        except Exception:
            pass
        return
    wait = check_rate_limit(msg.author.id)
    if wait > 0:
        try:
            await msg.reply(f"⏳ Chờ `{wait}s`.", mention_author=False)
        except Exception:
            pass
        return
    cd = check_cooldown(msg.author.id)
    if cd > 0:
        await asyncio.sleep(cd)
    uid = msg.author.id
    async with get_lock(cid, uid):
        try:
            h = await load_memory(cid, uid)
            persona = await get_persona_cached(cid, uid)
            code_mode = await get_mode_cached(cid) == "code"
            if not persona:
                if is_admin(msg.author):
                    persona = ("Người này là đàn em/anh em của bố. Gọi 'ái khanh', "
                               "'hiền hữu'. Xưng 'Trẫm', 'Ta', 'Bố'.")
                else:
                    persona = ("Thằng này là phàm phu, sâu bọ, dân đen. "
                               "Xưng 'Bố', 'Bố mày', 'Trẫm', 'Ta'. "
                               "Gọi 'phàm phu', 'thần dân', 'sâu bọ', 'khanh'. "
                               "Ngạo nghễ, uy nghi. Chửi tục 100%.")
            ocr = ""
            ftxt = ""
            if OCR_OK and msg.attachments:
                for att in msg.attachments:
                    if att.content_type and att.content_type.startswith("image/"):
                        try:
                            s = await http()
                            async with s.get(att.url,
                                             timeout=aiohttp.ClientTimeout(total=10)) as r:
                                if r.status == 200:
                                    buf = io.BytesIO(await r.read())
                                    img = Image.open(buf)
                                    ocr = await asyncio.get_running_loop().run_in_executor(
                                        executor, pytesseract.image_to_string, img, "vie+eng")
                                    img.close()
                                    buf.close()
                        except Exception:
                            pass
                        break
                    elif att.filename.endswith(".txt"):
                        try:
                            s = await http()
                            async with s.get(att.url,
                                             timeout=aiohttp.ClientTimeout(total=10)) as r:
                                if r.status == 200:
                                    ftxt = (await r.text())[:30000]
                        except Exception:
                            pass
            if _is_human_on(cid):
                reply_fn = lambda x: reply_as_human(msg, x)
            else:
                reply_fn = lambda x: msg.reply(x, mention_author=False)
            if ocr:
                h.append({"role": "user",
                          "content": "OCR:\n```\n" + ocr[:3000] + "\n```\n" +
                                     (content or "phân tích")})
            elif ftxt:
                h.append({"role": "user",
                          "content": f"[txt]\n```\n{ftxt}\n```\n{content}"})
            else:
                h.append({"role": "user", "content": content})
            full, _ = await push_stream(ai_stream(h, cid, uid, persona, code_mode),
                                         random.choice([Say.WAIT, Say.WAIT2, Say.WAIT3]),
                                         reply_fn)
            h.append({"role": "assistant", "content": full})
            if len(h) >= MAX_MEMORY:
                body = "\n".join(f"{m['role']}: {m['content'][:200]}" for m in h[:6])
                sm = None
                if GEMINI_KEYS:
                    try:
                        sm_payload = {"contents": [{"role": "user",
                                                     "parts": [{"text": f"Tóm tắt ngắn:\n{body}"}]}],
                                      "generationConfig": {"temperature": 0.4,
                                                            "maxOutputTokens": 250}}
                        sm, _ = await gemini_gen(sm_payload, timeout=15, max_rounds=1)
                    except Exception:
                        pass
                if not sm:
                    sm = "hội thoại trước"
                if len(sm) > 350:
                    sm = sm[:350] + "..."
                h = h[6:]
                prefix = f"[Ký ức]: {sm}"
                if h and h[0]["role"] == "user":
                    h[0]["content"] = f"{prefix}\n\n{h[0]['content']}"
                else:
                    h.insert(0, {"role": "user", "content": prefix})
            await save_memory(cid, uid, h)
        except discord.errors.Forbidden:
            log.warning("không reply ch=%s", msg.channel.id)
        except discord.errors.NotFound:
            log.warning("msg xóa ch=%s", msg.channel.id)
        except Exception as e:
            log.error("on_message: %s", e)
            try:
                await msg.reply(random.choice([Say.ERR, Say.ERR2]),
                                mention_author=False)
            except Exception:
                pass


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        raw = ctx.message.content.strip()
        if not raw.startswith("!"):
            return
        parts = raw[1:].split(maxsplit=1)
        if not parts:
            return
        cmd = parts[0].lower()
        near = difflib.get_close_matches(cmd, [c.name for c in bot.commands],
                                          n=3, cutoff=0.5)
        e = discord.Embed(title="⚔️  TRẪM ĐÉO BAN LỆNH NÀY",
                          description=f"`!{cmd}` — Chiếu chỉ này đéo tồn tại, sâu bọ.",
                          color=ROYAL_RED)
        if near:
            e.add_field(name="🎯 Ý ngươi là",
                        value="\n".join(f"⚜️ `!{s}`" for s in near), inline=False)
        else:
            e.add_field(name="📜", value="Gõ `!lhelp`.", inline=False)
        try:
            await ctx.reply(embed=e, mention_author=False)
        except Exception:
            pass
        return
    if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
        cn = ctx.command.name if ctx.command else "?"
        try:
            await ctx.reply(f"⚔️ `!{cn}` sai tham số. Gõ `!lhelp`",
                            mention_author=False)
        except Exception:
            pass
        return
    cn = ctx.command.name if ctx.command else "?"
    log.error("[%s]: %s", cn, error)
    try:
        await ctx.reply(f"⚔️ `!{cn}` lỗi: `{str(error)[:200]}`",
                        mention_author=False)
    except Exception:
        pass


async def shutdown():
    try:
        await close_http()
    except Exception:
        pass
    try:
        save_counters_sync()
    except Exception:
        pass


def start_bot():
    if not TOKEN:
        log.error("thiếu DISCORD_TOKEN")
        return
    if not GEMINI_KEYS and not GROQ_KEYS:
        log.error("thiếu GEMINI_KEY hoặc GROQ_KEY")
        return
    if not OWNER:
        log.warning("⚠️ OWNER (CRE_ID) chưa set")
    log.info("BÁ VƯƠNG ĐẠI ĐẾ v9.4 khởi động (TOOLS BÁ VƯƠNG)")
    log.info("UVLOOP=%s · ORJSON=%s", UVLOOP, JSON_FAST)
    log.info("Gemini: %d keys · Groq: %d keys", len(GEMINI_KEYS), len(GROQ_KEYS))
    log.info("Owner: %s · Human: %s", OWNER or "chưa set", HUMAN_NAME)
    if VOICE_RECV_OK:
        log.info("Voice Chat: OK")
    else:
        log.warning("Voice Chat: LỖI — %s", VOICE_RECV_ERR or "không rõ")
    try:
        bot.run(TOKEN, log_handler=None)
    except KeyboardInterrupt:
        log.info("Ctrl+C")
    except discord.errors.LoginFailure:
        log.error("token sai")
    except Exception as e:
        log.error("lỗi: %s", e)
    finally:
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(shutdown())
            loop.close()
        except Exception:
            pass
        try:
            executor.shutdown(wait=False, cancel_futures=True)
            scan_executor.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass
        log.info("Đã thoát")


log.info("tools.py v9.4 BLOCK 2/2 — Crypto + Util + Fun + Autodel + Tasks + Events loaded")