# ============================================================
# voice_part1.py — Config + Music (SoundCloud Primary) + Voice TTS + VoiceChat
# v8.1 — NO PROXY, SoundCloud primary, PO Token + Client Spoofing
# ============================================================

_counter_dirty = False


async def save_counters():
    global _counter_dirty
    _counter_dirty = True


@tasks.loop(seconds=5)
async def flush_counters_task():
    global _counter_dirty
    if _counter_dirty:
        try:
            await asyncio.get_running_loop().run_in_executor(None, save_counters_sync)
            _counter_dirty = False
        except Exception:
            pass


# ============================================================
# MUSIC — YTDL (v8.1 — SoundCloud Primary + NO PROXY)
# ✅ PO Token Provider
# ✅ Client Spoofing (web_embedded, mweb, tv)
# ✅ Smart Fallback: SoundCloud → YouTube
# ✅ Auto-update yt-dlp
# ✅ KHÔNG cần proxy, KHÔNG cần cookie
# ============================================================

POT_PROVIDER_URL = os.getenv("POT_PROVIDER_URL", "http://127.0.0.1:4416").strip()
USE_YOUTUBE_FALLBACK = os.getenv("YOUTUBE_FALLBACK", "1") == "1"
SC_CLIENT_ID = os.getenv("SC_CLIENT_ID", "").strip()

YDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
    "extract_flat": False,
    "geo_bypass": True,
    "no_color": True,
    "sleep_requests": 1.5,
    "sleep_interval": 2,
    "max_sleep_interval": 5,
    "retries": 5,
    "fragment_retries": 5,
    "file_access_retries": 3,
    "extractor_retries": 3,
    "http_headers": {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Sec-Fetch-Mode": "navigate",
    },
    "soundcloud_formats": "http_aac,hls_aac,http_opus,hls_opus,http_mp3",
    "extractor_args": {
        "youtubepot-bgutilhttp": {
            "base_url": [POT_PROVIDER_URL],
        },
        "youtube": {
            "player_client": ["web_embedded", "mweb", "tv"],
            "player_skip": ["webpage", "configs"],
        },
        "soundcloud": {
            "formats": ["http_aac", "hls_aac", "http_mp3"],
        },
    },
    "remote_components": ["ejs:github"],
    "logger": None,
}

if SC_CLIENT_ID:
    YDL_OPTS["extractor_args"]["soundcloud"] = {
        "client_id": [SC_CLIENT_ID],
        "formats": ["http_aac", "hls_aac", "http_mp3"],
    }

FFMPEG_MUSIC = {
    "options": "-vn -loglevel quiet",
    "before_options": (
        "-reconnect 1 -reconnect_streamed 1 "
        "-reconnect_delay_max 5 -nostdin"
    ),
}

ydl = None
if YTDL_OK:
    try:
        ydl = yt_dlp.YoutubeDL(YDL_OPTS)
        log.info("[MUSIC] yt-dlp OK — SoundCloud primary + YouTube fallback (NO PROXY)")
    except Exception as e:
        log.error("[MUSIC] Không khởi tạo được yt-dlp: %s", e)
        ydl = None


def _auto_update_ytdlp():
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade",
             "--no-cache-dir", "yt-dlp"],
            capture_output=True, timeout=120, text=True,
        )
        if result.returncode == 0:
            log.info("[MUSIC] yt-dlp updated OK")
        else:
            log.warning("[MUSIC] yt-dlp update fail: %s",
                        result.stderr[-300:] if result.stderr else "?")
    except Exception as e:
        log.warning("[MUSIC] yt-dlp auto-update error: %s", e)


if YTDL_OK:
    threading.Thread(target=_auto_update_ytdlp, daemon=True).start()


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title", "unknown")
        self.duration = data.get("duration", 0)
        self.thumbnail = data.get("thumbnail", "")
        self.uploader = data.get("uploader", "")
        self.webpage_url = data.get("webpage_url", "")

    @classmethod
    async def from_url(cls, url, stream=True):
        if not ydl:
            raise Exception("yt-dlp chưa cài hoặc khởi tạo lỗi")
        loop = asyncio.get_running_loop()

        def extract():
            return ydl.extract_info(url, download=not stream)

        data = await loop.run_in_executor(executor, extract)
        if data is None:
            raise Exception("không extract được")
        if "entries" in data:
            if not data["entries"]:
                raise Exception("không có entry")
            data = data["entries"][0]

        fn = data.get("url")
        if stream and "formats" in data:
            af = [
                f for f in data["formats"]
                if f.get("acodec") not in (None, "none")
                and f.get("vcodec") in (None, "none")
            ]
            if af:
                af.sort(
                    key=lambda x: (x.get("abr") or 0, x.get("tbr") or 0),
                    reverse=True,
                )
                fn = af[0].get("url", fn)

        if not fn:
            raise Exception("không có URL stream")

        return cls(
            discord.FFmpegPCMAudio(fn, executable=FFMPEG_BIN, **FFMPEG_MUSIC),
            data=data,
        )


def fmt_dur(sec):
    if not sec:
        return "?:??"
    try:
        sec = int(sec)
    except Exception:
        return "?:??"
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _detect_platform(url):
    u = (url or "").lower()
    if "soundcloud.com" in u:
        return "SoundCloud"
    if "youtube.com" in u or "youtu.be" in u:
        return "YouTube"
    return "Unknown"


def _try_extract(query):
    try:
        return ydl.extract_info(query, download=False)
    except Exception as e:
        log.debug("[MUSIC] extract '%s' fail: %s", query[:60], str(e)[:150])
        return None


def _normalize_info(data, original_query):
    if not data:
        return None
    if "entries" in data:
        entries = data.get("entries") or []
        if not entries:
            return None
        data = entries[0]
    if not data:
        return None
    url = data.get("webpage_url") or data.get("url") or original_query
    return {
        "title": data.get("title", "unknown"),
        "url": url,
        "duration": data.get("duration", 0),
        "thumbnail": data.get("thumbnail", ""),
        "uploader": data.get("uploader", ""),
        "platform": _detect_platform(url),
    }


def track_info(query, is_url=False):
    if not ydl:
        return None
    if is_url:
        data = _try_extract(query)
        return _normalize_info(data, query)
    data = _try_extract(f"scsearch1:{query}")
    info = _normalize_info(data, query)
    if info:
        return info
    if USE_YOUTUBE_FALLBACK:
        log.info("[MUSIC] SoundCloud miss '%s' → fallback YouTube", query)
        data = _try_extract(f"ytsearch1:{query}")
        info = _normalize_info(data, query)
        if info:
            return info
    return None


async def play_next(guild, vc, _attempt=0):
    st = mstate(guild.id)

    if _attempt > 3:
        log.error("play_next: bỏ cuộc sau %d lần retry — clear queue", _attempt)
        st["current"] = None
        st["queue"].clear()
        st["loop_count"] = st["loop_max"] = 0
        ch = bot.get_channel(st.get("text_channel") or 0)
        if ch:
            try:
                await ch.send("💀 Nhạc gãy liên tục, tao dẹp queue.")
            except Exception:
                pass
        return

    if _attempt == 0:
        if st["current"] and st["loop_max"] > 0 and st["loop_count"] < st["loop_max"]:
            st["loop_count"] += 1
            track = st["current"]
        elif st["queue"]:
            track = st["queue"].pop(0)
            st["current"] = track
            st["loop_count"] = 0
            if st["loop_max"] > 0:
                st["loop_count"] = 1
        else:
            st["current"] = None
            st["loop_count"] = st["loop_max"] = 0
            try:
                await vc.disconnect()
            except Exception:
                pass
            return
    else:
        track = st["current"]
        if not track:
            return

    if not vc or not vc.is_connected():
        log.warning("play_next: voice client không còn connected")
        st["current"] = None
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        log.error("play_next: không lấy được loop")
        return

    try:
        player = await YTDLSource.from_url(track["url"], stream=True)
    except Exception as e:
        log.error("play_next attempt %d extract fail [%s]: %s",
                  _attempt, track.get("platform", "?"), str(e)[:200])
        await asyncio.sleep(1.5)
        return await play_next(guild, vc, _attempt + 1)

    if not vc.is_connected():
        log.warning("play_next: vc disconnected trong lúc extract")
        st["current"] = None
        return

    try:
        player.volume = st.get("volume", 0.5)
    except Exception:
        pass

    _fired = {"done": False}

    def after(err):
        if _fired["done"]:
            return
        _fired["done"] = True
        if err:
            log.error("player error: %s", err)
        try:
            if loop and not loop.is_closed() and loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    play_next(guild, vc, 0), loop)
        except Exception as e:
            log.error("schedule next: %s", e)

    try:
        vc.play(player, after=after)
    except Exception as e:
        log.error("vc.play fail: %s", e)
        _fired["done"] = True
        await asyncio.sleep(0.8)
        return await play_next(guild, vc, _attempt + 1)

    ch = bot.get_channel(st.get("text_channel") or 0)
    if ch:
        e = discord.Embed(title="🎵  NHẠC CUNG", color=ROYAL_GOLD)
        e.add_field(name="⚜️ Khúc", value=player.title[:100], inline=False)
        e.add_field(name="⏱️ Dài", value=fmt_dur(player.duration), inline=True)
        e.add_field(name="🔊 Âm", value=f"{int(st['volume']*100)}%", inline=True)
        platform = track.get("platform", "?")
        e.add_field(name="🌐 Nguồn", value=f"`{platform}`", inline=True)
        if player.thumbnail:
            e.set_thumbnail(url=player.thumbnail)
        try:
            await ch.send(embed=e)
        except Exception:
            pass


@bot.command(name="play", aliases=["p"])
async def cmd_play(ctx, *, query: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not YTDL_OK:
        await ctx.reply("Chưa cài yt-dlp.")
        return
    if not FFMPEG_BIN:
        await ctx.reply("Chưa cài ffmpeg.")
        return
    if not query:
        await ctx.reply("Dùng: `!play <tên/link>` hoặc `!play a, b, c`")
        return
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.reply("Vào voice trước.")
        return

    queries = [q.strip() for q in query.split(",") if q.strip()]
    target = ctx.author.voice.channel
    vc = ctx.voice_client

    async with ctx.typing():
        try:
            if vc and vc.is_connected():
                if vc.channel != target:
                    await vc.move_to(target)
            else:
                vc = await target.connect()

            st = mstate(ctx.guild.id)
            st["text_channel"] = ctx.channel.id
            loop = asyncio.get_running_loop()
            added = 0
            sc_count = 0
            yt_count = 0

            for q in queries[:20]:
                is_url = q.startswith("http")
                try:
                    info = await loop.run_in_executor(
                        executor,
                        lambda qq=q, uu=is_url: track_info(qq, uu),
                    )
                except Exception as e:
                    log.error("play extract: %s", e)
                    continue
                if not info:
                    continue
                st["queue"].append({**info, "requester": ctx.author.display_name})
                added += 1
                if info.get("platform") == "SoundCloud":
                    sc_count += 1
                elif info.get("platform") == "YouTube":
                    yt_count += 1

            if added == 0:
                await ctx.reply("Không tìm thấy bài nào (SoundCloud + YouTube).")
                return

            msg = f"Thêm {added} bài vào queue."
            if sc_count or yt_count:
                parts = []
                if sc_count:
                    parts.append(f"☁️ {sc_count} SoundCloud")
                if yt_count:
                    parts.append(f"▶️ {yt_count} YouTube")
                msg += f" ({' · '.join(parts)})"

            if vc.is_playing() or vc.is_paused():
                await ctx.send(msg)
            else:
                await ctx.send(msg + " Bắt đầu phát.")
                await play_next(ctx.guild, vc)

        except Exception as e:
            log.error("cmd_play: %s", e)
            await ctx.reply(f"Lỗi: {str(e)[:150]}")


@bot.command(name="queue", aliases=["q"])
async def cmd_queue(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.guild:
        return
    st = mstate(ctx.guild.id)
    if not st["queue"] and not st["current"]:
        await ctx.reply("Queue rỗng.")
        return
    e = discord.Embed(title="🎵  QUEUE", color=ROYAL_GOLD)
    if st["current"]:
        p = st["current"].get("platform", "?")
        e.add_field(
            name="Đang phát",
            value=f"{st['current']['title'][:80]} · `{p}`",
            inline=False,
        )
    if st["queue"]:
        lines = []
        for i, t in enumerate(st["queue"][:15], 1):
            p = t.get("platform", "?")
            lines.append(f"{i}. [{p}] {t['title'][:70]}")
        e.add_field(
            name=f"Tiếp ({len(st['queue'])})",
            value="\n".join(lines),
            inline=False,
        )
    await ctx.send(embed=e)


@bot.command(name="skip")
async def cmd_skip(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    vc = ctx.voice_client
    if vc and (vc.is_playing() or vc.is_paused()):
        st = mstate(ctx.guild.id)
        st["loop_count"] = st["loop_max"] = 0
        vc.stop()
        await ctx.message.add_reaction("⏭️")
    else:
        await ctx.reply("Không có gì phát.")


@bot.command(name="pause")
async def cmd_pause(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.message.add_reaction("⏸️")
    elif vc and vc.is_paused():
        vc.resume()
        await ctx.message.add_reaction("▶️")


@bot.command(name="stopmusic")
async def cmd_stopmusic(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    vc = ctx.voice_client
    if vc:
        st = mstate(ctx.guild.id)
        st["queue"].clear()
        st["current"] = None
        st["loop_count"] = st["loop_max"] = 0
        vc.stop()
        await ctx.send("Dừng nhạc.")


@bot.command(name="loop")
async def cmd_loop(ctx, count: int = 3):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    st = mstate(ctx.guild.id)
    count = max(0, min(50, count))
    st["loop_count"] = 0
    st["loop_max"] = count
    await ctx.send("Tắt loop." if count == 0 else f"Loop {count} lần.")


@bot.command(name="nowplaying", aliases=["np"])
async def cmd_nowplaying(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.guild:
        return
    st = mstate(ctx.guild.id)
    if not st["current"]:
        await ctx.reply("Không có gì đang phát.")
        return
    t = st["current"]
    p = t.get("platform", "?")
    e = discord.Embed(title="🎧  ĐANG PHÁT", color=ROYAL_GOLD)
    e.add_field(name="Bài", value=t["title"][:100], inline=False)
    e.add_field(name="Dài", value=fmt_dur(t.get("duration", 0)), inline=True)
    e.add_field(name="Nguồn", value=f"`{p}`", inline=True)
    if t.get("thumbnail"):
        e.set_thumbnail(url=t["thumbnail"])
    await ctx.send(embed=e)


@bot.command(name="volume", aliases=["vol"])
async def cmd_volume(ctx, value: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.guild:
        return
    st = mstate(ctx.guild.id)
    if not value:
        await ctx.reply(f"🔊 Volume: `{int(st.get('volume', 0.5) * 100)}%`")
        return
    v = value.lower().strip()
    try:
        if v.endswith("x"):
            vol = float(v.rstrip("x").replace(",", "."))
        else:
            n = float(v.replace(",", "").rstrip("%"))
            vol = n / 100 if n > 3 else n
        vol = max(0.0, min(3.0, vol))
    except Exception:
        await ctx.reply("Số sai. VD: `!volume 1.5` hoặc `!volume 150%`")
        return
    st["volume"] = vol
    vc = ctx.voice_client
    if vc and vc.source and hasattr(vc.source, "volume"):
        try:
            vc.source.volume = vol
        except Exception:
            pass
    await ctx.send(f"🔊 Volume → `{int(vol * 100)}%`")


# ============================================================
# TTS — SPEAK
# ============================================================
def _parse_speak_args(content):
    preset = "nam"
    speed = 1.0
    text = content.strip()
    for _ in range(5):
        low = text.lower()
        first = low.split(None, 1)[0] if low.split() else ""
        p = PRESET_ALIASES.get(first, first)
        if p in VOICE_PRESETS:
            preset = p
            text = text[len(first):].strip()
            continue
        m = re.match(r"^(\d+(?:[.,]\d+)?)\s*[xX]\s+", text)
        if m:
            try:
                speed = max(0.1, min(4.0, float(m.group(1).replace(",", "."))))
            except Exception:
                pass
            text = text[m.end():].strip()
            continue
        break
    return preset, speed, text


@bot.command(name="join", aliases=["j", "vao"])
async def cmd_join(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.reply("Vào voice trước.")
        return
    target = ctx.author.voice.channel
    vc = ctx.voice_client
    try:
        if vc and vc.is_connected():
            if vc.channel != target:
                await vc.move_to(target)
                await ctx.send(f"Chuyển sang {target.name}.")
            else:
                await ctx.send(f"Đang ở {target.name} rồi.")
        else:
            await target.connect()
            await ctx.send(f"Vào {target.name} rồi.")
    except Exception as e:
        await ctx.reply(f"Lỗi: {str(e)[:200]}")


@bot.command(name="speak")
async def cmd_speak(ctx, *, text: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not TTS_OK:
        await ctx.reply("Chưa cài edge-tts.")
        return
    if not FFMPEG_BIN:
        await ctx.reply("Chưa cài ffmpeg.")
        return
    if not text:
        presets = ", ".join(sorted(VOICE_PRESETS.keys()))
        await ctx.reply(f"Dùng: `!speak [preset] [Nx] <text>`\nPreset: {presets}")
        return
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.reply("Vào voice trước.")
        return
    preset, speed, content = _parse_speak_args(text)
    if not content:
        await ctx.reply("Chưa có nội dung.")
        return
    cfg = VOICE_PRESETS[preset]
    final_speed = max(0.1, min(4.0, speed * cfg["rate_mult"]))
    rate_str = f"{int(round((final_speed - 1.0) * 100)):+d}%"
    pitch_str = cfg.get("pitch", "+0Hz")
    target = ctx.author.voice.channel
    vc = ctx.voice_client
    raw = processed = None
    try:
        if vc and vc.is_connected():
            if vc.channel != target:
                await vc.move_to(target)
        else:
            vc = await target.connect()
        voice = cfg["voice"]
        lang = detect_lang_heuristic(content)
        if lang != "vi" and lang in VOICE_MAP and preset in ("nam", "nu", "namtre", "tre", "gia"):
            v = VOICE_MAP[lang]
            voice = v[0] if preset in ("nam", "namtre", "gia") else v[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        raw = tmp.name
        tmp.close()
        await edge_tts.Communicate(content, voice, rate=rate_str, pitch=pitch_str).save(raw)
        processed = raw + ".proc.mp3"
        filt = cfg.get("filter")
        cmd = ([FFMPEG_BIN, "-y", "-i", raw, "-filter:a", filt, "-vn", "-loglevel", "error", processed]
               if filt else [FFMPEG_BIN, "-y", "-i", raw, "-vn", "-loglevel", "error", processed])
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=30)
        if r.returncode != 0 or not os.path.exists(processed):
            try:
                if os.path.exists(processed):
                    os.remove(processed)
            except Exception:
                pass
            processed = raw
        elif os.path.exists(raw) and processed != raw:
            try:
                os.remove(raw)
            except Exception:
                pass
        if not os.path.exists(processed):
            await ctx.reply("Không tạo được file.")
            return
        if vc.is_playing():
            vc.stop()

        def after(err):
            try:
                if processed and os.path.exists(processed):
                    os.remove(processed)
            except Exception:
                pass

        vc.play(discord.FFmpegPCMAudio(processed, executable=FFMPEG_BIN,
                                        options="-vn -loglevel quiet"), after=after)
        try:
            await ctx.message.add_reaction("🎙️")
        except Exception:
            pass
        await ctx.send(f"`{preset}` · `{lang}` · `{voice}` · `{final_speed:.2f}x`")
    except Exception as e:
        log.error("speak: %s", e)
        await ctx.reply(f"Lỗi: {str(e)[:200]}")


@bot.command(name="stop")
async def cmd_stop(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Dừng rồi.")


@bot.command(name="leave")
async def cmd_leave(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Rời voice.")


# ============================================================
# VOICE CHAT (Speech-to-Text + TTS)
# ============================================================
_whisper_model = None
_whisper_tried = False
_whisper_lock = threading.Lock()


def _load_whisper():
    global _whisper_model, _whisper_tried
    with _whisper_lock:
        if _whisper_model is not None:
            return _whisper_model
        _whisper_tried = True
        try:
            from faster_whisper import WhisperModel
            log.info("Loading Whisper base...")
            _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
            log.info("Whisper loaded OK")
        except ImportError as e:
            log.error("Whisper ImportError: %s", e)
            _whisper_model = None
        except Exception as e:
            log.error("Whisper load fail: %s", e)
            _whisper_model = None
    return _whisper_model


if VOICE_RECV_OK:
    class VoiceChatSink(voice_recv.AudioSink):
        def __init__(self, guild_id, text_channel_id, owner_id):
            super().__init__()
            self.guild_id = guild_id
            self.text_channel_id = text_channel_id
            self.owner_id = owner_id
            self.buffers = {}
            self.last_packet = {}
            self.start_time = {}
            self.user_objs = {}
            self.lock = threading.Lock()

        def wants_opus(self):
            return False

        def write(self, user, data):
            try:
                if not user or user.id != self.owner_id:
                    return
                pcm = getattr(data, "pcm", None)
                if not pcm:
                    return
                uid = user.id
                now = time.time()
                with self.lock:
                    if uid not in self.buffers:
                        self.buffers[uid] = bytearray()
                        self.start_time[uid] = now
                    self.buffers[uid].extend(pcm)
                    self.last_packet[uid] = now
                    self.user_objs[uid] = user
            except Exception:
                pass

        def cleanup(self):
            with self.lock:
                self.buffers.clear()
                self.last_packet.clear()
                self.start_time.clear()
                self.user_objs.clear()
else:
    VoiceChatSink = None


def _clean_for_tts(text):
    if not text:
        return ""
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_~]+", "", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    text = re.sub(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2700-\u27BF]", "", text)
    text = re.sub(r"[\u200d\uFE0F]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:400]


async def _voice_stt(pcm_bytes):
    if not pcm_bytes or len(pcm_bytes) < 48000:
        return ""
    raw_wav = converted = None
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        raw_wav = tmp.name
        tmp.close()
        with wave.open(raw_wav, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            wf.writeframes(pcm_bytes)
        if FFMPEG_BIN:
            converted = raw_wav + ".16k.wav"
            r = subprocess.run(
                [FFMPEG_BIN, "-y", "-i", raw_wav, "-ar", "16000", "-ac", "1",
                 "-f", "wav", "-loglevel", "error", converted],
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=15)
            if r.returncode != 0 or not os.path.exists(converted):
                converted = raw_wav
        else:
            converted = raw_wav
        loop = asyncio.get_running_loop()
        model = await loop.run_in_executor(executor, _load_whisper)
        if model:
            def _w():
                try:
                    segments, _ = model.transcribe(converted, language="vi", beam_size=3,
                                                    vad_filter=True, condition_on_previous_text=False)
                    return " ".join(s.text for s in segments).strip()
                except Exception:
                    return ""
            text = await loop.run_in_executor(executor, _w)
            if text and len(text) > 1:
                return text
        if SR_OK:
            def _g():
                try:
                    r = sr.Recognizer()
                    r.energy_threshold = 300
                    r.dynamic_energy_threshold = True
                    with sr.AudioFile(converted) as src:
                        audio = r.record(src)
                    return r.recognize_google(audio, language="vi-VN")
                except Exception:
                    return ""
            return await loop.run_in_executor(executor, _g) or ""
        return ""
    except Exception as e:
        log.error("_voice_stt: %s", e)
        return ""
    finally:
        for p in (converted, raw_wav):
            try:
                if p and os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass


_VOICE_MUSIC_KEYWORDS = ["mở nhạc", "mở bài", "phát nhạc", "phát bài", "play",
                         "bật nhạc", "bật bài", "cho tao nghe", "cho t nghe",
                         "nghe nhạc", "nghe bài", "mở đi", "phát đi", "hát"]
_VOICE_MUSIC_STOP = ["tắt nhạc", "dừng nhạc", "stop nhạc", "stop music",
                     "ngừng nhạc", "tắt bài", "dừng bài", "tắt đi", "stop đi", "tắt"]
_VOICE_MUSIC_SKIP = ["skip", "bài tiếp", "next bài", "chuyển bài", "đổi bài"]
_VOICE_MUSIC_PAUSE = ["tạm dừng", "pause", "dừng lại", "hold"]
_VOICE_MUSIC_JOIN = ["vào voice", "vô voice", "join voice"]
_VOICE_MUSIC_LEAVE = ["ra khỏi voice", "thoát voice", "leave voice"]


def _detect_voice_command(text):
    if not text:
        return None, None
    low = text.lower().strip()
    for kw in _VOICE_MUSIC_STOP:
        if kw in low:
            return "stop_music", None
    for kw in _VOICE_MUSIC_SKIP:
        if kw in low:
            return "skip", None
    for kw in _VOICE_MUSIC_PAUSE:
        if kw in low:
            return "pause", None
    for kw in _VOICE_MUSIC_LEAVE:
        if kw in low:
            return "leave", None
    for kw in _VOICE_MUSIC_JOIN:
        if kw in low:
            return "join", None
    for kw in _VOICE_MUSIC_KEYWORDS:
        if kw in low:
            idx = low.find(kw)
            arg = text[idx + len(kw):].strip()
            arg = re.sub(r"^(cho tao|cho t|đi|nhé|đi mà|nhạc|bài|một bài|1 bài)\s+", "", arg, flags=re.I)
            arg = re.sub(r"^(tên|tựa|của|bài)\s+", "", arg, flags=re.I)
            return "play", (arg.strip(",.!? ") or None)
    return None, None


async def _voice_ai_reply(text):
    try:
        gid = 0
        hist = _voice_history.setdefault(gid, [])
        hist.append({"role": "user", "content": text})
        if len(hist) > 6:
            hist[:] = hist[-6:]
        msgs = [{"role": "system", "content": VOICE_PROMPT}] + hist
        reply = ""
        if GROQ_KEYS:
            r, _ = await groq_gen(msgs, json_mode=False, timeout=15,
                                   temperature=1.05, max_tokens=300)
            if r and not is_refusal(r[:200]):
                reply = r.strip()
        if not reply and GEMINI_KEYS:
            payload = {"contents": [{"role": "user", "parts": [{"text": text}]}],
                       "systemInstruction": {"parts": [{"text": VOICE_PROMPT}]},
                       "generationConfig": {"temperature": 1.05, "maxOutputTokens": 300},
                       "safetySettings": safety()}
            t, _ = await gemini_gen(payload, timeout=15, max_rounds=1)
            if t and not is_refusal(t[:200]):
                reply = t.strip()
        if not reply:
            reply = _R.choice(["đm mày nói gì đấy con", "im mẹ mồm đi bố đang nghe",
                                "cút mẹ mày đi, bố đéo rảnh", "đm nghe rõ chưa thằng lol",
                                "bố đéo hiểu mày nói cái lz gì"])
        reply = _clean_for_tts(reply)
        hist.append({"role": "assistant", "content": reply})
        return reply
    except Exception:
        return "đm lag rồi"


async def _voice_tts_play(vc, text):
    if not TTS_OK or not FFMPEG_BIN or not text:
        return
    raw = processed = None
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        raw = tmp.name
        tmp.close()
        await edge_tts.Communicate(text, "vi-VN-NamMinhNeural",
                                    rate="+0%", pitch="+0Hz").save(raw)
        processed = raw + ".proc.mp3"
        r = subprocess.run([FFMPEG_BIN, "-y", "-i", raw, "-vn", "-loglevel", "error", processed],
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=30)
        if r.returncode != 0 or not os.path.exists(processed):
            processed = raw
        wait_start = time.time()
        while vc.is_playing() and time.time() - wait_start < 30:
            await asyncio.sleep(0.2)

        def after(err):
            for p in (raw, processed):
                try:
                    if p and os.path.exists(p):
                        os.remove(p)
                except Exception:
                    pass

        if vc.is_connected():
            vc.play(discord.FFmpegPCMAudio(processed, executable=FFMPEG_BIN,
                                            options="-vn -loglevel quiet"), after=after)
    except Exception:
        pass


async def _voice_handle_music(vc, guild_id, text_channel_id, action, arg):
    st = mstate(guild_id)
    st["text_channel"] = text_channel_id
    if action == "stop_music":
        st["queue"].clear()
        st["current"] = None
        st["loop_count"] = st["loop_max"] = 0
        if vc.is_playing() or vc.is_paused():
            vc.stop()
        return "Đã tắt nhạc."
    if action == "skip":
        if vc.is_playing() or vc.is_paused():
            st["loop_count"] = st["loop_max"] = 0
            vc.stop()
            return "Đã chuyển bài."
        return "Không có gì phát."
    if action == "pause":
        if vc.is_playing():
            vc.pause()
            return "Đã tạm dừng."
        elif vc.is_paused():
            vc.resume()
            return "Tiếp tục."
        return "Không có gì phát."
    if action == "play":
        if not arg:
            return "Muốn mở gì?"
        try:
            loop = asyncio.get_running_loop()
            info = await loop.run_in_executor(executor, lambda q=arg: track_info(q, False))
            if not info:
                return "Không tìm được."
            st["queue"].append({**info, "requester": "owner_voice"})
            if not (vc.is_playing() or vc.is_paused()):
                guild = bot.get_guild(guild_id)
                asyncio.create_task(play_next(guild, vc))
            return f"Đang mở {info['title'][:60]}."
        except Exception:
            return "Lỗi tìm bài."
    return None


async def _handle_voice_input(guild_id, user_id, user_name, pcm_bytes, text_channel_id):
    if _voice_processing.get(guild_id):
        return
    _voice_processing[guild_id] = True
    try:
        try:
            text = await _voice_stt(pcm_bytes)
        except Exception:
            return
        if not text or len(text.strip()) < 2:
            return
        log.info("Voice [%s]: %s", user_name, text)
        vc = None
        for c in bot.voice_clients:
            if c.guild.id == guild_id:
                vc = c
                break
        if not vc or not vc.is_connected():
            return
        action, arg = _detect_voice_command(text)
        ch = bot.get_channel(text_channel_id)
        if ch:
            try:
                await ch.send(f"**{user_name}**: {text}")
            except Exception:
                pass
        if action:
            if action == "leave":
                try:
                    await vc.disconnect()
                except Exception:
                    pass
                _voice_chat_active[guild_id] = False
                _voice_chat_active.pop(f"{guild_id}_owner", None)
                return
            if action == "join":
                return
            result = await _voice_handle_music(vc, guild_id, text_channel_id, action, arg)
            if ch and result:
                try:
                    await ch.send(f"**Bot**: {result}")
                except Exception:
                    pass
            if result:
                await _voice_tts_play(vc, result)
            return
        reply = await _voice_ai_reply(text)
        if ch:
            try:
                await ch.send(f"**Bot**: {reply}")
            except Exception:
                pass
        await _voice_tts_play(vc, reply)
        await asyncio.sleep(_VOICE_COOLDOWN)
    except Exception as e:
        log.error("_handle_voice_input: %s", e)
    finally:
        _voice_processing[guild_id] = False


@tasks.loop(seconds=0.5)
async def voice_watcher_task():
    for gid in list(_voice_chat_active.keys()):
        if not isinstance(gid, int):
            continue
        if not _voice_chat_active.get(gid):
            continue
        if _voice_processing.get(gid):
            continue
        owner_id = _voice_chat_active.get(f"{gid}_owner")
        if not owner_id:
            continue
        vc = None
        for c in bot.voice_clients:
            if c.guild.id == gid:
                vc = c
                break
        if not vc or not VOICE_RECV_OK or not isinstance(vc, voice_recv.VoiceRecvClient):
            continue
        sink = getattr(vc, "_sink", None)
        if not sink or not hasattr(sink, "buffers"):
            continue
        now = time.time()
        to_process = []
        with sink.lock:
            for uid in list(sink.buffers.keys()):
                if uid != owner_id:
                    sink.buffers.pop(uid, None)
                    sink.last_packet.pop(uid, None)
                    sink.start_time.pop(uid, None)
                    sink.user_objs.pop(uid, None)
                    continue
                last = sink.last_packet.get(uid, 0)
                started = sink.start_time.get(uid, now)
                duration = now - started
                if (now - last > _VOICE_SILENCE and duration > _VOICE_MIN_SEC) or \
                   (duration > _VOICE_MAX_SEC):
                    buf = bytes(sink.buffers.pop(uid, b""))
                    user = sink.user_objs.pop(uid, None)
                    sink.last_packet.pop(uid, None)
                    sink.start_time.pop(uid, None)
                    if user and len(buf) > 48000:
                        to_process.append((uid, user.display_name, buf))
        for uid, uname, buf in to_process:
            tc = getattr(vc, "_voice_text_channel", 0)
            asyncio.create_task(_handle_voice_input(gid, uid, uname, buf, tc))
            break


@bot.command(name="voicechat", aliases=["vc", "talk", "noichuyen"])
async def cmd_voicechat(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not is_owner(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not VOICE_RECV_OK:
        await ctx.reply(f"❌ Thiếu `discord-ext-voice-recv`.\n`{VOICE_RECV_ERR}`")
        return
    if not TTS_OK:
        await ctx.reply("❌ Thiếu `edge-tts`.")
        return
    if not ctx.guild:
        return
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.reply("🎧 Vào voice trước.")
        return
    gid = ctx.guild.id
    if _voice_chat_active.get(gid):
        _voice_chat_active[gid] = False
        _voice_chat_active.pop(f"{gid}_owner", None)
        vc = ctx.voice_client
        if vc and isinstance(vc, voice_recv.VoiceRecvClient):
            try:
                vc.stop_listening()
            except Exception:
                pass
        await ctx.send("🔕 Tắt.")
        return
    target = ctx.author.voice.channel
    vc = ctx.voice_client
    try:
        if vc and not isinstance(vc, voice_recv.VoiceRecvClient):
            try:
                await vc.disconnect(force=True)
            except Exception:
                pass
            vc = None
            await asyncio.sleep(0.5)
        if vc and vc.is_connected():
            if vc.channel != target:
                await vc.move_to(target)
        else:
            vc = await target.connect(cls=voice_recv.VoiceRecvClient)
        vc._voice_text_channel = ctx.channel.id
        sink = VoiceChatSink(gid, ctx.channel.id, ctx.author.id)
        vc.listen(sink)
        _voice_chat_active[gid] = True
        _voice_chat_active[f"{gid}_owner"] = ctx.author.id
        _voice_processing[gid] = False
        _voice_history[gid] = []
        if not voice_watcher_task.is_running():
            voice_watcher_task.start()
        e = discord.Embed(title="👑  BỐ GIÁNG THẾ VOICE  👑", color=ROYAL_GOLD)
        e.add_field(name="⚔️ Động", value=target.mention, inline=False)
        e.add_field(name="👑 Đế vương", value=ctx.author.mention, inline=False)
        e.add_field(name="📜 Khẩu lệnh",
                    value="`mở nhạc <tên>` · `tắt nhạc` · `skip` · `tạm dừng` · `ra khỏi voice`",
                    inline=False)
        await ctx.send(embed=e)
    except Exception as ex:
        log.error("voicechat: %s", ex)
        await ctx.reply(f"💀 Lỗi: {str(ex)[:300]}")


@bot.command(name="stopvc", aliases=["stopvoicechat"])
async def cmd_stopvc(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not is_owner(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.guild:
        return
    gid = ctx.guild.id
    _voice_chat_active[gid] = False
    _voice_chat_active.pop(f"{gid}_owner", None)
    vc = ctx.voice_client
    if vc and VOICE_RECV_OK and isinstance(vc, voice_recv.VoiceRecvClient):
        try:
            vc.stop_listening()
        except Exception:
            pass
    await ctx.send("Đã tắt voice chat.")


@bot.command(name="vcstatus")
async def cmd_vcstatus(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.guild:
        return
    gid = ctx.guild.id
    active = _voice_chat_active.get(gid, False)
    e = discord.Embed(title="🎙️  VOICE CHAT STATUS", color=ROYAL_GOLD)
    e.add_field(name="Trạng thái", value="BẬT" if active else "TẮT", inline=True)
    e.add_field(name="STT", value="Whisper" if _whisper_model else ("Google" if SR_OK else "Không có"), inline=True)
    e.add_field(name="voice_recv", value="OK" if VOICE_RECV_OK else "LỖI", inline=True)
    e.add_field(name="TTS", value="OK" if TTS_OK else "Không có", inline=True)
    await ctx.send(embed=e)


@bot.command(name="whispertest")
async def cmd_whispertest(ctx):
    if not is_owner(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    global _whisper_model
    _whisper_model = None
    st = await ctx.send("🔄 Loading Whisper...")
    try:
        import sys as _sys
        info = f"Python: `{_sys.executable}`"
        model = await asyncio.get_running_loop().run_in_executor(executor, _load_whisper)
        if model:
            await st.edit(content=f"✅ Whisper OK\n{info}")
        else:
            await st.edit(content=f"❌ Whisper fail\n{info}")
    except Exception as e:
        await st.edit(content=f"❌ Lỗi: `{str(e)[:200]}`")


log.info("VOICE PART 1 v8.1 OK — Music SoundCloud + Voice TTS + VoiceChat")
# ============================================================
# voice_part2.py — Deobf + Obfuscate + Realtime + AI + Admin + Util
# v8.1
# ============================================================

# ============================================================
# DEOBF
# ============================================================
DEOBF_SYSTEM = wrap_prompt(
    "Senior reverse engineer. Auto-detect: Python/JS/Java/C/Lua/PHP/Go/PowerShell, "
    "base64, hex, gzip, zlib, XOR, ROT13, JWT, obfuscated, minified, packed.\n"
    "Decode fully, recursively. Output JSON ONLY: "
    "{\"explanation\":\"<vi>\",\"format\":\"<detected>\",\"fixed_code\":\"<decoded>\"}")


async def deobf_ai(data, filename=""):
    if not data:
        return None, "rỗng"
    text = data[:60000] if isinstance(data, str) else data.decode("utf-8", errors="ignore")[:60000]
    prompt = f"Filename: {filename}\n\n=== INPUT ===\n{text}\n=== END ===\n\nDecode. Output JSON."
    msgs = [{"role": "system", "content": DEOBF_SYSTEM}, {"role": "user", "content": prompt}]
    for _ in GROQ_MODELS[:3]:
        try:
            r, _ = await groq_gen(msgs, json_mode=True, timeout=90, temperature=0.1, max_tokens=8192)
            if r and not is_refusal(r[:400]):
                return r, None
        except Exception:
            continue
    if GEMINI_KEYS:
        payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                   "systemInstruction": {"parts": [{"text": DEOBF_SYSTEM}]},
                   "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json",
                                        "maxOutputTokens": 8192},
                   "safetySettings": safety()}
        for _ in range(2):
            r, _ = await gemini_gen(payload, timeout=90, max_rounds=1)
            if r and not is_refusal(r[:400]):
                return r, None
    return None, "all failed"


def deobf_local(data):
    if not data:
        return None
    text = data.strip() if isinstance(data, str) else data.decode("utf-8", errors="ignore").strip()
    out = []
    try:
        c = re.sub(r"\s+", "", text)
        if re.fullmatch(r"[A-Za-z0-9+/=]+", c) and len(c) > 8:
            d = base64.b64decode(c + "=" * (-len(c) % 4)).decode("utf-8", errors="ignore")
            if d and d.isprintable():
                out.append(("base64", d[:2000]))
    except Exception:
        pass
    try:
        c = re.sub(r"\s+", "", text)
        if re.fullmatch(r"[0-9a-fA-F]+", c) and len(c) % 2 == 0 and len(c) > 8:
            d = bytes.fromhex(c).decode("utf-8", errors="ignore")
            if d and d.isprintable():
                out.append(("hex", d[:2000]))
    except Exception:
        pass
    try:
        import codecs
        d = codecs.decode(text, "rot_13")
        if d and d != text and any(ch.isalpha() for ch in d):
            out.append(("rot13", d[:2000]))
    except Exception:
        pass
    return out


@bot.command(name="deobf", aliases=["deob", "decode", "unpack", "clean"])
async def cmd_deobf(ctx, *, req: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    data = ""
    filename = ""
    if ctx.message.attachments:
        att = ctx.message.attachments[0]
        filename = att.filename
        try:
            s = await http()
            async with s.get(att.url, timeout=40) as r:
                if r.status != 200:
                    await ctx.reply(f"HTTP {r.status}")
                    return
                raw = await r.read()
        except Exception as e:
            await ctx.reply(f"Lỗi: {str(e)[:200]}")
            return
        try:
            data = raw.decode("utf-8")
        except UnicodeDecodeError:
            try:
                data = raw.decode("latin-1")
            except Exception:
                data = base64.b64encode(raw).decode("ascii")
                filename += ".b64"
    elif req:
        data = req
        filename = "text_input"
    elif ctx.message.reference:
        try:
            ref = ctx.message.reference
            if ref.resolved and isinstance(ref.resolved, discord.Message):
                data = ref.resolved.content or ""
                filename = "reply"
        except Exception:
            pass
    if not data or len(data.strip()) < 4:
        await ctx.reply("Dùng: `!deobf` + file / text / reply")
        return
    async with ctx.typing():
        status = await ctx.send(f"Đang phân tích `{filename}` ({len(data)} ký tự)...")
        try:
            raw_result, err = await deobf_ai(data, filename)
        except Exception as e:
            raw_result, err = None, str(e)[:200]
        obj = None
        if raw_result:
            try:
                t = raw_result.strip()
                if t.startswith("```json"):
                    t = t[7:-3].strip()
                elif t.startswith("```"):
                    t = t[3:-3].strip()
                obj = json.loads(t)
            except Exception:
                ex = extract_json(raw_result)
                if ex:
                    try:
                        obj = json.loads(ex)
                    except Exception:
                        pass
        if not obj:
            local = deobf_local(data)
            if local:
                lines = [f"[{fmt}] {content}" for fmt, content in local]
                obj = {"explanation": "Local decode: " + ", ".join(f for f, _ in local),
                       "format": local[0][0],
                       "fixed_code": "\n\n".join(lines)}
            else:
                try:
                    await status.edit(content=f"Không decode được: `{(err or 'unknown')[:200]}`")
                except Exception:
                    pass
                return
        explanation = obj.get("explanation", "không có mô tả")
        fmt = obj.get("format", "unknown")
        result = (obj.get("fixed_code") or obj.get("code") or obj.get("content") or "").strip()
        if not result:
            try:
                await status.edit(content="Kết quả rỗng.")
            except Exception:
                pass
            return
        try:
            await status.delete()
        except Exception:
            pass
        e = discord.Embed(title="🔓  DEOBFUSCATION", color=ROYAL_GOLD)
        e.add_field(name="File", value=f"`{filename}`", inline=True)
        e.add_field(name="Format", value=f"`{fmt}`", inline=True)
        e.add_field(name="Size", value=f"{len(data):,}b → {len(result):,}b", inline=True)
        e.add_field(name="Mô tả", value=explanation[:1020], inline=False)
        await ctx.send(embed=e)
        if len(result) < 1900:
            await ctx.send(f"```\n{result}\n```")
        else:
            fb = io.BytesIO(result.encode("utf-8"))
            await ctx.send(content=f"File cho {ctx.author.mention}:",
                           file=discord.File(fb, filename=f"decoded_{filename}.txt"))
            fb.close()


# ============================================================
# OBFUSCATE
# ============================================================
OBF_SYSTEM = wrap_prompt(
    "Senior red team engineer specializing in PAYLOAD OBFUSCATION.\n"
    "Take clean code → obfuscated variant that bypasses WAF/AV.\n"
    "Output ONLY JSON: "
    '{"explanation":"<vi>","language":"<python|bash|ps|php|js>",'
    '"technique":"<...>","obfuscated":"<payload>","original":"<input>"}')


def _obf_local(data):
    if not data:
        return None
    results = {}
    text = data if isinstance(data, str) else data.decode("utf-8", errors="ignore")
    try:
        results["base64"] = base64.b64encode(text.encode("utf-8")).decode("ascii")
    except Exception:
        pass
    try:
        results["hex"] = text.encode("utf-8").hex()
    except Exception:
        pass
    try:
        results["rot13"] = __import__("codecs").encode(text, "rot_13")
    except Exception:
        pass
    try:
        codes = ",".join(str(ord(c)) for c in text)
        results["charcodes_python"] = f"exec(''.join(chr(c) for c in [{codes}]))"
    except Exception:
        pass
    try:
        rev = text[::-1]
        results["reverse_b64"] = base64.b64encode(rev.encode()).decode()
    except Exception:
        pass
    try:
        key = random.randint(1, 255)
        xored = bytes(b ^ key for b in text.encode("utf-8"))
        enc = base64.b64encode(xored).decode()
        results["xor_b64"] = (f"# XOR key = {key}\nimport base64\n"
                              f"data = base64.b64decode('{enc}')\n"
                              f"exec(bytes(b ^ {key} for b in data).decode())")
    except Exception:
        pass
    try:
        results["bash_b64"] = f'echo {base64.b64encode(text.encode()).decode()} | base64 -d | bash'
    except Exception:
        pass
    try:
        utf16 = text.encode("utf-16-le")
        ps = base64.b64encode(utf16).decode()
        results["powershell_enc"] = f"powershell -EncodedCommand {ps}"
    except Exception:
        pass
    try:
        codes = ",".join(str(ord(c)) for c in text)
        results["js_eval"] = f"eval(String.fromCharCode({codes}))"
    except Exception:
        pass
    return results


@bot.command(name="obf", aliases=["obfuscate", "encode", "ma-hoa", "pack"])
async def cmd_obf(ctx, *, req: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    data = ""
    filename = ""
    use_ai = False
    if req and req.strip().startswith(("-ai", "--ai")):
        use_ai = True
        req = req.strip()[3:].strip() if req.strip().startswith("-ai") else req.strip()[5:].strip()
    if ctx.message.attachments:
        att = ctx.message.attachments[0]
        filename = att.filename
        try:
            s = await http()
            async with s.get(att.url, timeout=40) as r:
                if r.status != 200:
                    await ctx.reply(f"HTTP {r.status}")
                    return
                raw = await r.read()
            try:
                data = raw.decode("utf-8")
            except UnicodeDecodeError:
                data = raw.decode("latin-1", errors="ignore")
        except Exception as e:
            await ctx.reply(f"Lỗi: {str(e)[:200]}")
            return
    elif req:
        data = req
        filename = "text_input"
    if not data or len(data.strip()) < 3:
        await ctx.reply("Dùng: `!obf <text>` hoặc `!obf -ai <text>`")
        return
    async with ctx.typing():
        status = await ctx.send(f"Đang obf `{filename}` ({len(data)}b)...")
        if not use_ai:
            variants = _obf_local(data)
            if not variants:
                try:
                    await status.edit(content="Không obf được.")
                except Exception:
                    pass
                return
            try:
                await status.delete()
            except Exception:
                pass
            e = discord.Embed(title="🎭  OBFUSCATION", color=ROYAL_GOLD)
            e.description = f"Input: {len(data)}b · Kỹ thuật: {len(variants)}"
            for name, content in list(variants.items())[:10]:
                val = str(content)
                if len(val) > 1000:
                    val = val[:990] + "..."
                e.add_field(name=name, value=f"```\n{val}\n```", inline=False)
            await ctx.send(embed=e)
            return
        prompt = f"=== PAYLOAD ===\n{data[:40000]}\n=== END ===\n\nReturn JSON."
        msgs = [{"role": "system", "content": OBF_SYSTEM}, {"role": "user", "content": prompt}]
        raw_result = None
        for _ in GROQ_MODELS[:3]:
            try:
                r, _ = await groq_gen(msgs, json_mode=True, timeout=90, temperature=0.2, max_tokens=8192)
                if r and not is_refusal(r[:400]):
                    raw_result = r
                    break
            except Exception:
                pass
        if not raw_result and GEMINI_KEYS:
            payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                       "systemInstruction": {"parts": [{"text": OBF_SYSTEM}]},
                       "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json",
                                            "maxOutputTokens": 8192},
                       "safetySettings": safety()}
            for _ in range(2):
                r, _ = await gemini_gen(payload, timeout=90, max_rounds=1)
                if r and not is_refusal(r[:400]):
                    raw_result = r
                    break
        obj = None
        if raw_result:
            try:
                t = raw_result.strip()
                if t.startswith("```json"):
                    t = t[7:-3].strip()
                elif t.startswith("```"):
                    t = t[3:-3].strip()
                obj = json.loads(t)
            except Exception:
                ex = extract_json(raw_result)
                if ex:
                    try:
                        obj = json.loads(ex)
                    except Exception:
                        pass
        if not obj:
            variants = _obf_local(data)
            obj = {"explanation": "Fallback local.",
                   "language": "auto", "technique": "multi",
                   "obfuscated": "\n\n".join(f"[{k}]\n{v}" for k, v in list(variants.items())[:6])}
        try:
            await status.delete()
        except Exception:
            pass
        explanation = obj.get("explanation", "")
        lang = obj.get("language", "?")
        tech = obj.get("technique", "?")
        obf = (obj.get("obfuscated") or "").strip()
        e = discord.Embed(title="🎭  AI OBFUSCATION", description=explanation[:1500], color=ROYAL_GOLD)
        e.add_field(name="Language", value=f"`{lang}`", inline=True)
        e.add_field(name="Technique", value=f"`{tech}`", inline=True)
        e.add_field(name="Size", value=f"`{len(data)}b → {len(obf)}b`", inline=True)
        await ctx.send(embed=e)
        if obf:
            if len(obf) < 1900:
                await ctx.send(f"```\n{obf}\n```")
            else:
                fb = io.BytesIO(obf.encode("utf-8"))
                await ctx.send(content=f"File obf cho {ctx.author.mention}:",
                               file=discord.File(fb, filename=f"obf_{filename}.txt"))
                fb.close()


# ============================================================
# REALTIME — WEATHER / CRYPTO / CURRENCY / WIKI / NEWS / IP
# ============================================================
_WEATHER_CITY_CACHE = {}
_VI_CITY_MAP = {
    "hồ chí minh": "Ho Chi Minh City", "ho chi minh": "Ho Chi Minh City",
    "hcm": "Ho Chi Minh City", "sài gòn": "Ho Chi Minh City", "sai gon": "Ho Chi Minh City",
    "hà nội": "Hanoi", "ha noi": "Hanoi", "hn": "Hanoi",
    "đà nẵng": "Da Nang", "da nang": "Da Nang",
    "cần thơ": "Can Tho", "huế": "Hue", "nha trang": "Nha Trang",
    "hải phòng": "Hai Phong", "biên hòa": "Bien Hoa"}


async def _geocode_city(city):
    key = city.lower().strip()
    if key in _VI_CITY_MAP:
        city = _VI_CITY_MAP[key]
        key = city.lower()
    if key in _WEATHER_CITY_CACHE:
        return _WEATHER_CITY_CACHE[key]
    s = await http()
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1&language=vi&format=json"
        async with s.get(url, timeout=10) as r:
            if r.status == 200:
                data = await r.json()
                results = data.get("results") or []
                if results:
                    g = results[0]
                    out = (g.get("latitude"), g.get("longitude"),
                           g.get("name") or city, g.get("country") or "")
                    _WEATHER_CITY_CACHE[key] = out
                    return out
    except Exception:
        pass
    return None


def _wmo_to_vi(code):
    try:
        code = int(code)
    except Exception:
        code = 0
    m = {0: ("☀️", "Trời quang"), 1: ("🌤️", "Ít mây"), 2: ("⛅", "Mây rải rác"),
         3: ("☁️", "Nhiều mây"), 45: ("🌫️", "Sương mù"), 48: ("🌫️", "Sương mù đóng băng"),
         51: ("🌦️", "Mưa phùn nhẹ"), 53: ("🌦️", "Mưa phùn"), 55: ("🌦️", "Mưa phùn dày"),
         61: ("🌧️", "Mưa nhỏ"), 63: ("🌧️", "Mưa vừa"), 65: ("🌧️", "Mưa to"),
         71: ("🌨️", "Tuyết nhẹ"), 73: ("🌨️", "Tuyết vừa"), 75: ("❄️", "Tuyết to"),
         80: ("🌦️", "Mưa rào nhẹ"), 81: ("🌧️", "Mưa rào"), 82: ("⛈️", "Mưa rào lớn"),
         95: ("⛈️", "Giông bão"), 96: ("⛈️", "Giông có mưa đá"), 99: ("⛈️", "Giông mưa đá lớn")}
    return m.get(code, ("🌤️", "Không rõ"))


async def tool_weather(city):
    geo = await _geocode_city(city)
    if not geo:
        return None
    lat, lon, name, country = geo
    s = await http()
    try:
        url = (f"https://api.open-meteo.com/v1/forecast?"
               f"latitude={lat}&longitude={lon}"
               f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
               f"precipitation,weather_code,wind_speed_10m,wind_direction_10m,surface_pressure,"
               f"visibility,uv_index&timezone=auto")
        async with s.get(url, timeout=15) as r:
            if r.status != 200:
                return None
            data = await r.json()
        cur = data.get("current") or {}
        code = cur.get("weather_code", 0)
        emoji, desc = _wmo_to_vi(code)
        return {"city": name, "country": country,
                "temp": cur.get("temperature_2m", "?"),
                "feels": cur.get("apparent_temperature", "?"),
                "humidity": cur.get("relative_humidity_2m", "?"),
                "wind": cur.get("wind_speed_10m", "?"),
                "desc": desc, "uv": cur.get("uv_index", "?"),
                "vis": cur.get("visibility", "?"),
                "pressure": cur.get("surface_pressure", "?"),
                "emoji": emoji}
    except Exception:
        return None


async def tool_crypto(coins=None):
    if not coins:
        coins = ["bitcoin", "ethereum", "binancecoin", "solana", "ripple"]
    s = await http()
    try:
        ids = ",".join(coins)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,vnd&include_24hr_change=true"
        async with s.get(url, timeout=15) as r:
            if r.status == 200:
                return await r.json()
    except Exception:
        pass
    return None


async def tool_currency(amount=1, frm="USD", to="VND"):
    s = await http()
    try:
        url = f"https://open.er-api.com/v6/latest/{frm.upper()}"
        async with s.get(url, timeout=15) as r:
            if r.status != 200:
                return None
            data = await r.json()
        rate = data.get("rates", {}).get(to.upper())
        if not rate:
            return None
        return {"from": frm.upper(), "to": to.upper(), "rate": rate,
                "amount": amount, "result": amount * rate,
                "updated": data.get("time_last_update_utc", "?")}
    except Exception:
        return None


async def tool_wiki(term, lang="vi"):
    if not term or not term.strip():
        return None
    term = term.strip()
    s = await http()
    title = None
    try:
        search_api = f"https://{lang}.wikipedia.org/w/api.php"
        params = {"action": "query", "list": "search", "srsearch": term,
                  "format": "json", "srlimit": "1", "srprop": ""}
        async with s.get(search_api, params=params, timeout=12,
                         headers={"User-Agent": "DiscordBot/1.0"}) as r:
            if r.status == 200:
                data = await r.json()
                results = data.get("query", {}).get("search", [])
                if results:
                    title = results[0].get("title")
    except Exception:
        pass
    if not title:
        title = term
    try:
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
        async with s.get(url, timeout=12, allow_redirects=True,
                         headers={"User-Agent": "DiscordBot/1.0"}) as r:
            if r.status != 200:
                return None
            data = await r.json()
        extract = (data.get("extract") or "").strip()
        if not extract:
            return None
        return {"title": data.get("title", title), "extract": extract,
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "thumb": data.get("thumbnail", {}).get("source", ""), "lang": lang}
    except Exception:
        return None


async def _wiki_search_fallback(term):
    s = await http()
    for lang in ("vi", "en"):
        try:
            api = f"https://{lang}.wikipedia.org/w/api.php"
            params = {"action": "opensearch", "search": term, "limit": "1",
                      "namespace": "0", "format": "json"}
            async with s.get(api, params=params, timeout=10,
                             headers={"User-Agent": "DiscordBot/1.0"}) as r:
                if r.status == 200:
                    data = await r.json()
                    if len(data) > 1 and data[1]:
                        title = data[1][0]
                        surl = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
                        async with s.get(surl, timeout=10,
                                         headers={"User-Agent": "DiscordBot/1.0"}) as r2:
                            if r2.status == 200:
                                d = await r2.json()
                                extract = (d.get("extract") or "").strip()
                                if extract:
                                    return {"title": d.get("title", title), "extract": extract,
                                            "url": d.get("content_urls", {}).get("desktop", {}).get("page", ""),
                                            "thumb": d.get("thumbnail", {}).get("source", ""), "lang": lang}
        except Exception:
            continue
    return None


async def tool_news(topic=None, source="vnexpress"):
    sources = {
        "vnexpress": "https://vnexpress.net/rss/tin-moi-nhat.rss",
        "tuoitre": "https://tuoitre.vn/rss/tin-moi-nhat.rss",
        "thanhnien": "https://thanhnien.vn/rss/home.rss",
        "dantri": "https://dantri.com.vn/rss/home.rss",
        "24h": "https://www.24h.com.vn/upload/rss/tintuctonghop.rss"}
    if source and (source.startswith("http://") or source.startswith("https://")):
        url = source
        if not url.endswith(".rss") and "rss" not in url.lower():
            base = url.rstrip("/")
            if "vnexpress" in base:
                url = "https://vnexpress.net/rss/tin-moi-nhat.rss"
            elif "tuoitre" in base:
                url = "https://tuoitre.vn/rss/tin-moi-nhat.rss"
            elif "thanhnien" in base:
                url = "https://thanhnien.vn/rss/home.rss"
            elif "dantri" in base:
                url = "https://dantri.com.vn/rss/home.rss"
            else:
                url = base + "/rss"
    else:
        url = sources.get(source, sources["vnexpress"])
    s = await http()
    try:
        async with s.get(url, timeout=20, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/rss+xml,application/xml,text/xml,*/*"}) as r:
            if r.status != 200:
                return None
            txt = await r.text()
        items = re.findall(
            r"<item>\s*<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>\s*(?:<[^>]+>\s*)*<link>(.*?)</link>",
            txt, re.DOTALL)
        if not items:
            items = re.findall(
                r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>.*?<link>(.*?)</link>",
                txt, re.DOTALL)
        out = []
        for title, link in items:
            title = re.sub(r"<[^>]+>", "", title).strip()
            link = link.strip()
            if not title or not link:
                continue
            if topic and topic.lower() not in title.lower():
                continue
            out.append({"title": title[:200], "link": link})
        return out[:6] if out else None
    except Exception:
        return None


async def tool_ip(ip):
    s = await http()
    try:
        async with s.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,org,as,query,timezone,lat,lon", timeout=10) as r:
            if r.status == 200:
                return await r.json()
    except Exception:
        pass
    return None


def render_weather(d):
    e = discord.Embed(title=f"{d['emoji']}  THỜI TIẾT — {d['city']}, {d['country']}", color=ROYAL_GOLD)
    e.add_field(name="🌡️ Nhiệt độ", value=f"**{d['temp']}°C**", inline=True)
    e.add_field(name="🤔 Cảm giác", value=f"{d['feels']}°C", inline=True)
    e.add_field(name="💧 Độ ẩm", value=f"{d['humidity']}%", inline=True)
    e.add_field(name="💨 Gió", value=f"{d['wind']} km/h", inline=True)
    e.add_field(name="🌤️ Trời", value=d['desc'], inline=True)
    e.add_field(name="☀️ UV", value=d['uv'], inline=True)
    e.add_field(name="👁️ Tầm nhìn", value=f"{d['vis']} m", inline=True)
    e.add_field(name="📊 Áp suất", value=f"{d['pressure']} hPa", inline=True)
    return e


def render_crypto(data):
    e = discord.Embed(title="💰  CRYPTO", color=ROYAL_GOLD)
    icons = {"bitcoin": "🟠", "ethereum": "💎", "binancecoin": "🟡",
             "solana": "🟣", "ripple": "🔵"}
    names = {"bitcoin": "BTC", "ethereum": "ETH", "binancecoin": "BNB",
             "solana": "SOL", "ripple": "XRP"}
    for k, v in data.items():
        if not isinstance(v, dict):
            continue
        usd = v.get("usd", 0)
        vnd = v.get("vnd", 0)
        change = v.get("usd_24h_change", 0)
        icon = icons.get(k, "🔹")
        sym = names.get(k, k.upper())
        arrow = "📈" if change > 0 else "📉"
        e.add_field(name=f"{icon} {sym}",
                    value=f"**${usd:,}**\n₫{vnd:,.0f}\n{arrow} `{change:+.2f}%`", inline=True)
    return e


def render_currency(d):
    e = discord.Embed(title="💱  TỶ GIÁ", color=ROYAL_GOLD)
    e.add_field(name="Từ", value=f"**{d['amount']:,} {d['from']}**", inline=True)
    e.add_field(name="➜", value="💵", inline=True)
    e.add_field(name="Sang", value=f"**{d['result']:,.2f} {d['to']}**", inline=True)
    e.add_field(name="⚜️ Tỷ giá", value=f"1 {d['from']} = {d['rate']:,.2f} {d['to']}", inline=False)
    if d.get("updated"):
        e.set_footer(text=d['updated'])
    return e


def render_wiki(d):
    lang = d.get("lang", "vi").upper()
    e = discord.Embed(title=f"📖  {d['title']}",
                      description=d['extract'][:1500] or "*Không có mô tả.*",
                      url=d.get("url") or None, color=ROYAL_GOLD)
    if d.get("thumb"):
        e.set_thumbnail(url=d["thumb"])
    e.set_footer(text=f"Wikipedia {lang}")
    return e


def render_news(items, source="vnexpress"):
    e = discord.Embed(title=f"📰  TIN TỨC — {source.title() if 'http' not in source else 'Custom'}  📰",
                      color=ROYAL_GOLD)
    for i, item in enumerate(items[:6], 1):
        e.add_field(name=f"`{i}.` {item['title'][:90]}",
                    value=f"[Đọc tiếp ↳]({item['link']})", inline=False)
    return e


def render_ip(d):
    e = discord.Embed(title=f"🌐  ĐỊA CHỈ IP: {d.get('query', '?')}", color=ROYAL_GOLD)
    e.add_field(name="🌍 Quốc gia", value=d.get("country", "?"), inline=True)
    e.add_field(name="🏙️ Vùng", value=d.get("regionName", "?"), inline=True)
    e.add_field(name="📍 Thành phố", value=d.get("city", "?"), inline=True)
    e.add_field(name="📡 ISP", value=f"`{d.get('isp', '?')}`", inline=False)
    e.add_field(name="🏢 Org", value=f"`{d.get('org', '?')}`", inline=False)
    e.add_field(name="🔢 AS", value=f"`{d.get('as', '?')}`", inline=False)
    return e


@bot.command(name="thoitiet", aliases=["weather", "wt"])
async def cmd_weather(ctx, *, city: str = "Hanoi"):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    async with ctx.typing():
        d = await tool_weather(city)
        if not d:
            await ctx.reply("Không lấy được thời tiết.")
            return
        await ctx.send(embed=render_weather(d))


@bot.command(name="crypto", aliases=["coin", "btc"])
async def cmd_crypto(ctx, coin: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    coins = None
    if coin:
        mapping = {"btc": "bitcoin", "eth": "ethereum", "bnb": "binancecoin",
                   "sol": "solana", "xrp": "ripple"}
        coins = [mapping.get(coin.lower(), coin.lower())]
    async with ctx.typing():
        d = await tool_crypto(coins)
        if not d:
            await ctx.reply("Không lấy được crypto.")
            return
        await ctx.send(embed=render_crypto(d))


@bot.command(name="tygia", aliases=["rate", "currency", "doitien"])
async def cmd_currency(ctx, amount: float = 1, frm: str = "USD", to: str = "VND"):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    async with ctx.typing():
        d = await tool_currency(amount, frm, to)
        if not d:
            await ctx.reply("Không lấy được tỷ giá.")
            return
        await ctx.send(embed=render_currency(d))


@bot.command(name="wiki", aliases=["wikipedia", "tra", "w"])
async def cmd_wiki(ctx, *, term: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not term:
        await ctx.reply("Dùng: `!wiki <từ khoá>`")
        return
    term = term.strip()
    if len(term) < 2:
        await ctx.reply("Ngắn quá.")
        return
    async with ctx.typing():
        d = await tool_wiki(term, lang="vi")
        if not d:
            d = await tool_wiki(term, lang="en")
        if not d:
            d = await _wiki_search_fallback(term)
        if not d:
            await ctx.reply(f"❌ Không tìm thấy **{term}**.")
            return
        await ctx.send(embed=render_wiki(d))


@bot.command(name="news", aliases=["tin", "tintuc"])
async def cmd_news(ctx, source: str = "vnexpress"):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    async with ctx.typing():
        items = await tool_news(source=source)
        if not items:
            await ctx.reply("Không lấy được tin.")
            return
        await ctx.send(embed=render_news(items, source))


@bot.command(name="ip", aliases=["ipinfo"])
async def cmd_ip(ctx, ip: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ip:
        await ctx.reply("Dùng: `!ip <địa chỉ>`")
        return
    async with ctx.typing():
        d = await tool_ip(ip)
        if not d or d.get("status") != "success":
            await ctx.reply("Không lấy được.")
            return
        await ctx.send(embed=render_ip(d))


# ============================================================
# AI — ASK / TRANSLATE / SETROLE / MODE / DRAW / RESET
# ============================================================
@bot.command(name="ask", aliases=["hoi"])
async def cmd_ask(ctx, *, q: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not q:
        await ctx.reply("Dùng: `!ask <câu hỏi>`")
        return
    if is_prompt_injection(q):
        await ctx.reply("⚔️ Trẫm đéo tiếp.")
        return
    wait = check_rate_limit(ctx.author.id)
    if wait > 0:
        await ctx.reply(f"⏳ Chờ `{wait}s`.")
        return
    h = [{"role": "user", "content": q}]
    p = await get_persona_cached(ctx.channel.id, ctx.author.id)
    ic = await get_mode_cached(ctx.channel.id) == "code"
    await push_stream(ai_stream(h, ctx.channel.id, ctx.author.id, p, ic),
                      random.choice([Say.WAIT, Say.WAIT2, Say.WAIT3]), ctx.reply)


@bot.command(name="translate", aliases=["dich"])
async def cmd_translate(ctx, lang: str = None, *, text: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not lang or not text:
        await ctx.reply("Dùng: `!translate <lang> <text>`")
        return
    wait = check_rate_limit(ctx.author.id)
    if wait > 0:
        await ctx.reply(f"⏳ Chờ `{wait}s`.")
        return
    h = [{"role": "user", "content": f"Dịch sang {lang}:\n{text}"}]
    p = await get_persona_cached(ctx.channel.id, ctx.author.id)
    ic = await get_mode_cached(ctx.channel.id) == "code"
    await push_stream(ai_stream(h, ctx.channel.id, ctx.author.id, p, ic), "Đang dịch...", ctx.reply)


@bot.command(name="setrole", aliases=["role"])
async def cmd_setrole(ctx, *, persona: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    cid, uid = ctx.channel.id, ctx.author.id

    def clr():
        db_run("DELETE FROM history WHERE channel_id=? AND user_id=?", (cid, uid))

    if not persona:
        await set_persona(cid, uid, "")
        await asyncio.get_running_loop().run_in_executor(None, clr)
        invalidate_persona_cache(cid, uid)
        old = _locks.pop((cid, uid), None)
        if old and old["lock"].locked():
            try:
                old["lock"].release()
            except Exception:
                pass
        await ctx.send(Say.ROLE_RESET)
        return
    text = persona.strip()[:2000]
    if len(text) < 3:
        await ctx.reply("Ngắn quá.")
        return
    await set_persona(cid, uid, text)
    await asyncio.get_running_loop().run_in_executor(None, clr)
    invalidate_persona_cache(cid, uid)
    old = _locks.pop((cid, uid), None)
    if old and old["lock"].locked():
        try:
            old["lock"].release()
        except Exception:
            pass
    await ctx.send(embed=discord.Embed(title="🎭  NHẬP VAI XONG",
                                        description=text[:1500], color=ROYAL_GOLD))


@bot.command(name="mode")
async def cmd_mode(ctx, m: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not m:
        await ctx.reply(f"mode: `{await get_mode_cached(ctx.channel.id)}`")
        return
    m = m.lower()
    if m not in ("chat", "code"):
        await ctx.reply("chat hoặc code.")
        return
    await set_mode(ctx.channel.id, m)
    invalidate_mode_cache(ctx.channel.id)
    await ctx.send(f"Đổi mode `{m}`.")


@bot.command(name="draw", aliases=["img", "ve"])
async def cmd_draw(ctx, *, prompt: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not prompt:
        await ctx.reply("Dùng: `!draw <mô tả>`")
        return
    wait = check_rate_limit(ctx.author.id)
    if wait > 0:
        await ctx.reply(f"⏳ Chờ `{wait}s`.")
        return
    async with ctx.typing():
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true"
        try:
            s = await http()
            async with s.get(url, timeout=60) as r:
                if r.status == 200:
                    d = await r.read()
                    if len(d) > 1024:
                        await ctx.send(file=discord.File(io.BytesIO(d), filename="gen.png"))
                    else:
                        await ctx.send("Ảnh rỗng.")
                else:
                    await ctx.send(f"Lỗi {r.status}")
        except Exception as e:
            await ctx.send(f"Lỗi: {str(e)[:200]}")


@bot.command(name="reset", aliases=["clearmem"])
async def cmd_reset(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return

    def d():
        db_run("DELETE FROM history WHERE channel_id=? AND user_id=?",
               (ctx.channel.id, ctx.author.id))

    await asyncio.get_running_loop().run_in_executor(None, d)
    invalidate_persona_cache(ctx.channel.id, ctx.author.id)
    await ctx.send(f"Xoá memory của {ctx.author.mention}.")


@bot.command(name="clearuser")
async def cmd_clearuser(ctx, member: discord.Member = None):
    if not is_allowed(ctx.author) or not member:
        await ctx.reply(pick_perm_insult())
        return

    def d():
        db_run("DELETE FROM history WHERE channel_id=? AND user_id=?",
               (ctx.channel.id, member.id))

    await asyncio.get_running_loop().run_in_executor(None, d)
    await ctx.send(f"Xoá memory của {member.mention}.")


# ============================================================
# ADMIN
# ============================================================
@bot.command(name="addadmin")
async def cmd_addadmin(ctx, member: discord.Member = None, *, note: str = ""):
    if not is_admin(ctx.author) or not member:
        await ctx.reply(pick_perm_insult())
        return
    await asyncio.get_running_loop().run_in_executor(None, add_admin, member.id, ctx.author.id, note)
    audit(ctx.author.id, "addadmin", f"{member.id}")
    await ctx.send(Say.ADMIN_ADD.format(u=member.mention))


@bot.command(name="deladmin")
async def cmd_deladmin(ctx, member: discord.Member = None):
    if not is_admin(ctx.author) or not member or is_owner(member):
        await ctx.reply(pick_perm_insult())
        return
    await asyncio.get_running_loop().run_in_executor(None, del_admin, member.id)
    audit(ctx.author.id, "deladmin", str(member.id))
    await ctx.send(Say.ADMIN_DEL.format(u=member.mention))


@bot.command(name="adduser", aliases=["allowuser"])
async def cmd_adduser(ctx, member: discord.Member = None):
    if not is_admin(ctx.author) or not member:
        await ctx.reply(pick_perm_insult())
        return
    await asyncio.get_running_loop().run_in_executor(None, add_user, member.id, ctx.author.id)
    audit(ctx.author.id, "adduser", str(member.id))
    await ctx.send(Say.USER_ADD.format(u=member.mention))


@bot.command(name="deluser", aliases=["denyuser"])
async def cmd_deluser(ctx, member: discord.Member = None):
    if not is_admin(ctx.author) or not member or is_owner(member):
        await ctx.reply(pick_perm_insult())
        return
    await asyncio.get_running_loop().run_in_executor(None, del_user, member.id)
    audit(ctx.author.id, "deluser", str(member.id))
    await ctx.send(Say.USER_DEL.format(u=member.mention))


@bot.command(name="listadmin")
async def cmd_listadmin(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    rows = db_run("SELECT user_id, added_at, note FROM admins ORDER BY added_at DESC", many=True) or []
    e = discord.Embed(title="👑  ADMIN", color=ROYAL_RED)
    if OWNER:
        e.add_field(name="Owner", value=f"`{OWNER}`", inline=False)
    for uid, ts, note in rows[:20]:
        try:
            u = await bot.fetch_user(int(uid))
            nm = u.name
        except Exception:
            nm = f"ID:{uid}"
        d = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "?"
        e.add_field(name=nm, value=f"`{uid}` · {d}\n{note or ''}", inline=False)
    await ctx.send(embed=e)


@bot.command(name="listuser")
async def cmd_listuser(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    rows = db_run("SELECT user_id, added_at FROM users ORDER BY added_at DESC", many=True) or []
    e = discord.Embed(title="👥  USER", color=ROYAL_GOLD)
    if not rows:
        e.description = "Trống."
    else:
        for uid, ts in rows[:30]:
            try:
                u = await bot.fetch_user(int(uid))
                nm = u.name
            except Exception:
                nm = f"ID:{uid}"
            d = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "?"
            e.add_field(name=nm, value=f"`{uid}` · {d}", inline=False)
    await ctx.send(embed=e)


@bot.command(name="turnon")
async def cmd_turnon(ctx):
    if not is_admin(ctx.author) or isinstance(ctx.channel, discord.DMChannel):
        await ctx.reply(pick_perm_insult())
        return
    await set_channel_active(ctx.channel.id, 1)
    await ctx.send("Bật chat.")


@bot.command(name="turnoff")
async def cmd_turnoff(ctx):
    if not is_admin(ctx.author) or isinstance(ctx.channel, discord.DMChannel):
        await ctx.reply(pick_perm_insult())
        return
    await set_channel_active(ctx.channel.id, 0)
    await ctx.send("Tắt chat.")


@bot.command(name="resetwebhook")
async def cmd_resetwebhook(ctx):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    count = 0
    for ch in ctx.guild.channels:
        if isinstance(ch, (discord.TextChannel, discord.Thread)):
            _wh_pool.pop(ch.id, None)
            try:
                for wh in await ch.webhooks():
                    if (wh.name and wh.name.startswith(("BOT_FAKE", "AFK_RELAY"))
                            and wh.user and wh.user.id == bot.user.id):
                        try:
                            await wh.delete()
                            count += 1
                        except Exception:
                            pass
            except Exception:
                continue
    await ctx.send(f"Xoá `{count}` webhook.")


# ============================================================
# UTIL
# ============================================================
@bot.command(name="check", aliases=["quota"])
async def cmd_check(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    await reset_check()
    e = discord.Embed(title="⚡  QUOTA API", color=ROYAL_GOLD)
    if GEMINI_KEYS:
        for i in range(len(GEMINI_KEYS)):
            e.add_field(name=f"Gemini #{i+1}",
                        value=f"{gcnt[i] if i < len(gcnt) else 0}/{G_LIMIT}", inline=False)
    if GROQ_KEYS:
        for i in range(len(GROQ_KEYS)):
            e.add_field(name=f"Groq #{i+1}",
                        value=f"{qcnt[i] if i < len(qcnt) else 0}/{Q_LIMIT}", inline=False)
    e.add_field(name="Ngày", value=cur_day, inline=False)
    e.add_field(name="Admin?", value="có" if is_admin(ctx.author) else "không", inline=False)
    await ctx.send(embed=e)


@bot.command(name="dbstatus")
async def cmd_dbstatus(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return

    def q():
        sz = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
        h = db_run("SELECT COUNT(*) FROM history", one=True)
        u = db_run("SELECT COUNT(*) FROM users", one=True)
        a = db_run("SELECT COUNT(*) FROM admins", one=True)
        m = db_run("SELECT COUNT(*) FROM mirror_log", one=True)
        au = db_run("SELECT COUNT(*) FROM audit", one=True)
        return (sz / (1024 * 1024), h[0] if h else 0, u[0] if u else 0,
                a[0] if a else 0, m[0] if m else 0, au[0] if au else 0)

    sz, hm, u, a, m, au = await asyncio.get_running_loop().run_in_executor(None, q)
    e = discord.Embed(title="📊  DB STATUS", color=ROYAL_GOLD)
    e.add_field(name="Size", value=f"{sz:.3f} MB")
    e.add_field(name="Memories", value=str(hm))
    e.add_field(name="Users", value=str(u))
    e.add_field(name="Admins", value=str(a))
    e.add_field(name="Mirror log", value=str(m))
    e.add_field(name="Audit log", value=str(au))
    await ctx.send(embed=e)


@bot.command(name="auditlog")
async def cmd_auditlog(ctx, count: int = 15):
    if not is_owner(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    rows = db_run("SELECT user_id, action, detail, ts FROM audit ORDER BY id DESC LIMIT ?",
                  (max(1, min(50, count)),), many=True) or []
    if not rows:
        await ctx.reply("Chưa có log.")
        return
    e = discord.Embed(title="📜 AUDIT LOG", color=ROYAL_GOLD)
    for uid, action, detail, ts in rows:
        d = datetime.fromtimestamp(ts).strftime("%H:%M %d/%m")
        e.add_field(name=f"{action} · {d}",
                    value=f"`{uid}` {detail[:100]}", inline=False)
    await ctx.send(embed=e)


@bot.command(name="testapi")
async def cmd_testapi(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.reply("DM thôi.")
        return
    st = await ctx.send("Đang test API...")
    e = discord.Embed(title="🧪  TEST RESULT", color=ROYAL_GOLD)
    session = await http()
    if GEMINI_KEYS:
        payload = {"contents": [{"role": "user", "parts": [{"text": "Hi"}]}],
                   "generationConfig": {"maxOutputTokens": 5}}
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        for i, key in enumerate(GEMINI_KEYS):
            mk = f"`{key[:6]}...{key[-3:]}`" if len(key) > 10 else "`***`"
            try:
                async with session.post(url, json=payload,
                                        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                                        timeout=8) as r:
                    s = "OK" if r.status == 200 else ("quota" if r.status == 429 else f"lỗi {r.status}")
                    e.add_field(name=f"Gemini {i+1}", value=f"{mk} {s}", inline=False)
            except Exception:
                e.add_field(name=f"Gemini {i+1}", value=f"{mk} lỗi", inline=False)
    if GROQ_KEYS:
        for i, key in enumerate(GROQ_KEYS):
            mk = f"`{key[:6]}...{key[-3:]}`" if len(key) > 10 else "`***`"
            h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            s = "chết"
            for model in GROQ_MODELS:
                body = {"model": model, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5}
                try:
                    async with session.post("https://api.groq.com/openai/v1/chat/completions",
                                            json=body, headers=h, timeout=6) as r:
                        if r.status == 200:
                            s = f"OK {model}"
                            break
                        if r.status == 429:
                            s = f"quota {model}"
                            break
                except Exception:
                    continue
            e.add_field(name=f"Groq {i+1}", value=f"{mk} {s}", inline=False)
    try:
        await st.delete()
    except Exception:
        pass
    await ctx.send(embed=e)


@bot.command(name="ping", aliases=["pong"])
async def cmd_ping(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    e = discord.Embed(title="🏓  PONG", color=ROYAL_GOLD)
    e.add_field(name="Latency", value=f"`{round(bot.latency*1000)}ms`", inline=True)
    e.add_field(name="HTTP", value="OK" if _http and not _http.closed else "Down", inline=True)
    e.add_field(name="UVLOOP", value="✅" if UVLOOP else "❌", inline=True)
    e.add_field(name="ORJSON", value="✅" if JSON_FAST else "❌", inline=True)
    await ctx.send(embed=e)


log.info("VOICE PART 2 v8.1 OK — Deobf + Realtime + AI + Admin + Util")
