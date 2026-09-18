# music_player.py — MUSIC PLAYER + LYRICS v1.3
# ✅ FIX v1.3: Capture loop trong __init__ — KHÔNG crash sau bài đầu

import asyncio
import re
import io
import aiohttp
import discord

try:
    from logging import getLogger
    _mp_log = getLogger("bot")
except Exception:
    import logging
    _mp_log = logging.getLogger("bot")


# ============================================================
# LYRICS API — lrclib.net
# ============================================================
async def _fetch_lyrics(artist, title, duration=None):
    s = aiohttp.ClientSession()
    try:
        params = {"artist_name": artist or "", "track_name": title or ""}
        if duration:
            try:
                params["duration"] = int(duration)
            except Exception:
                pass
        async with s.get("https://lrclib.net/api/search", params=params,
                          timeout=aiohttp.ClientTimeout(total=15),
                          headers={"User-Agent": "DiscordBot/1.0"}) as r:
            if r.status != 200:
                return None
            data = await r.json()
            if not data:
                async with s.get("https://lrclib.net/api/search",
                                  params={"q": f"{artist} {title}".strip()},
                                  timeout=aiohttp.ClientTimeout(total=15),
                                  headers={"User-Agent": "DiscordBot/1.0"}) as r2:
                    if r2.status != 200:
                        return None
                    data = await r2.json()
                    if not data:
                        return None
            best = data[0]
            return {
                "plain": best.get("plainLyrics") or "",
                "synced": best.get("syncedLyrics") or "",
                "source": "lrclib.net",
                "track": best.get("trackName", title),
                "artist": best.get("artistName", artist),
                "duration": best.get("duration"),
            }
    except Exception:
        return None
    finally:
        try:
            await s.close()
        except Exception:
            pass


def _parse_lrc(lrc_text):
    if not lrc_text:
        return []
    lines = []
    pattern = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\](.*)")
    for raw in lrc_text.splitlines():
        m = pattern.match(raw.strip())
        if not m:
            continue
        mins = int(m.group(1))
        secs = float(m.group(2))
        text = m.group(3).strip()
        if text:
            lines.append((mins * 60 + secs, text))
    lines.sort(key=lambda x: x[0])
    return lines


# ============================================================
# LYRICS SENDER
# ============================================================
class _LyricsSender:
    _tasks = {}

    @classmethod
    def cancel(cls, guild_id):
        t = cls._tasks.pop(guild_id, None)
        if t and not t.done():
            try:
                t.cancel()
            except Exception:
                pass

    @classmethod
    async def start(cls, guild_id, channel, lrc_lines, start_offset=0.0):
        cls.cancel(guild_id)
        if not lrc_lines:
            return
        task = asyncio.create_task(
            cls._run(guild_id, channel, lrc_lines, start_offset))
        cls._tasks[guild_id] = task

    @classmethod
    async def _run(cls, guild_id, channel, lrc_lines, start_offset):
        try:
            loop = asyncio.get_running_loop()
            t0 = loop.time() - start_offset
            for ts, text in lrc_lines:
                now = loop.time() - t0
                wait = ts - now
                if wait > 0:
                    await asyncio.sleep(wait)
                elif wait < -3:
                    continue
                try:
                    await channel.send(
                        f"-# *{text}*",
                        allowed_mentions=discord.AllowedMentions.none())
                except discord.HTTPException as e:
                    if e.status == 429:
                        ra = getattr(e, "retry_after", 1.5) or 1.5
                        await asyncio.sleep(min(ra, 5.0))
                        continue
                    break
                except Exception:
                    break
        except asyncio.CancelledError:
            pass
        except Exception:
            pass


# ============================================================
# SELECT MENU
# ============================================================
class TrackSelect(discord.ui.Select):
    def __init__(self, tracks, player_view):
        self.tracks = tracks
        self.player_view = player_view
        options = []
        for i, t in enumerate(tracks[:25]):
            title = (t.get("title") or "?")[:90]
            dur = t.get("duration", 0)
            dur_str = ""
            if dur:
                try:
                    m, s = divmod(int(dur), 60)
                    dur_str = f" ({m}:{s:02d})"
                except Exception:
                    pass
            requester = (t.get("requester") or "?")[:30]
            options.append(discord.SelectOption(
                label=f"{i+1}. {title[:80]}",
                value=str(i),
                description=f"{dur_str} · {requester}"
            ))
        super().__init__(placeholder="🎵 Chọn bài để phát...",
                          min_values=1, max_values=1,
                          options=options, row=0)

    async def callback(self, interaction):
        if interaction.user.id != self.player_view.user_id:
            try:
                await interaction.response.send_message(
                    "Không phải player của bạn.", ephemeral=True)
            except Exception:
                pass
            return
        try:
            idx = int(self.values[0])
        except Exception:
            return
        if idx < 0 or idx >= len(self.tracks):
            try:
                await interaction.response.send_message(
                    "Bài không tồn tại.", ephemeral=True)
            except Exception:
                pass
            return
        track = self.tracks[idx]
        try:
            await interaction.response.defer()
        except Exception:
            return
        await self.player_view.play_track(interaction, track)


# ============================================================
# PLAYER VIEW
# ============================================================
class PlayerView(discord.ui.View):
    def __init__(self, bot_obj, guild, text_channel, tracks, user_id):
        super().__init__(timeout=1800)
        self.bot = bot_obj
        self.guild = guild
        self.text_channel = text_channel
        self.tracks = list(tracks) if tracks else []
        self.user_id = user_id

        # ✅ FIX v1.3: Capture loop
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = None

        if self.tracks:
            try:
                self.add_item(TrackSelect(self.tracks, self))
            except Exception:
                pass
        self._build_controls()

    async def on_timeout(self):
        try:
            _LyricsSender.cancel(self.guild.id)
        except Exception:
            pass

    def _build_controls(self):
        stop_btn = discord.ui.Button(
            label="⏹ Stop", style=discord.ButtonStyle.danger,
            custom_id=f"pstop_{self.user_id}", row=1)

        async def stop_cb(interaction):
            if interaction.user.id != self.user_id:
                try:
                    await interaction.response.send_message(
                        "Không phải player của bạn.", ephemeral=True)
                except Exception:
                    pass
                return
            try:
                vc = self.guild.voice_client
                if vc:
                    _LyricsSender.cancel(self.guild.id)
                    try:
                        st = mstate(self.guild.id)
                        st["queue"].clear()
                        st["current"] = None
                        st["loop_count"] = st["loop_max"] = 0
                    except Exception:
                        pass
                    vc.stop()
                await interaction.response.send_message("⏹ Đã dừng.", ephemeral=True)
            except Exception as e:
                try:
                    await interaction.response.send_message(
                        f"❌ `{str(e)[:100]}`", ephemeral=True)
                except Exception:
                    pass

        stop_btn.callback = stop_cb
        self.add_item(stop_btn)

        skip_btn = discord.ui.Button(
            label="⏭ Skip", style=discord.ButtonStyle.secondary,
            custom_id=f"pskip_{self.user_id}", row=1)

        async def skip_cb(interaction):
            if interaction.user.id != self.user_id:
                try:
                    await interaction.response.send_message(
                        "Không phải player của bạn.", ephemeral=True)
                except Exception:
                    pass
                return
            try:
                vc = self.guild.voice_client
                if vc and (vc.is_playing() or vc.is_paused()):
                    _LyricsSender.cancel(self.guild.id)
                    vc.stop()
                    await interaction.response.send_message("⏭ Skip.", ephemeral=True)
                else:
                    await interaction.response.send_message(
                        "Không có gì đang phát.", ephemeral=True)
            except Exception as e:
                try:
                    await interaction.response.send_message(
                        f"❌ `{str(e)[:100]}`", ephemeral=True)
                except Exception:
                    pass

        skip_btn.callback = skip_cb
        self.add_item(skip_btn)

        pause_btn = discord.ui.Button(
            label="⏸ Pause", style=discord.ButtonStyle.secondary,
            custom_id=f"ppause_{self.user_id}", row=1)

        async def pause_cb(interaction):
            if interaction.user.id != self.user_id:
                try:
                    await interaction.response.send_message(
                        "Không phải player của bạn.", ephemeral=True)
                except Exception:
                    pass
                return
            try:
                vc = self.guild.voice_client
                if vc and vc.is_playing():
                    vc.pause()
                    await interaction.response.send_message("⏸ Paused.", ephemeral=True)
                elif vc and vc.is_paused():
                    vc.resume()
                    await interaction.response.send_message("▶️ Resumed.", ephemeral=True)
                else:
                    await interaction.response.send_message(
                        "Không có gì đang phát.", ephemeral=True)
            except Exception as e:
                try:
                    await interaction.response.send_message(
                        f"❌ `{str(e)[:100]}`", ephemeral=True)
                except Exception:
                    pass

        pause_btn.callback = pause_cb
        self.add_item(pause_btn)

        vol_dn = discord.ui.Button(
            label="🔉 -", style=discord.ButtonStyle.secondary,
            custom_id=f"pvol_dn_{self.user_id}", row=1)

        async def vol_dn_cb(interaction):
            if interaction.user.id != self.user_id:
                try:
                    await interaction.response.send_message(
                        "Không phải player của bạn.", ephemeral=True)
                except Exception:
                    pass
                return
            try:
                st = mstate(self.guild.id)
                v = max(0.0, float(st.get("volume", 0.5)) - 0.1)
                st["volume"] = v
                vc = self.guild.voice_client
                if vc and vc.source and hasattr(vc.source, "volume"):
                    try:
                        vc.source.volume = v
                    except Exception:
                        pass
                await interaction.response.send_message(
                    f"🔉 Volume: `{int(v*100)}%`", ephemeral=True)
            except Exception as e:
                try:
                    await interaction.response.send_message(
                        f"❌ `{str(e)[:100]}`", ephemeral=True)
                except Exception:
                    pass

        vol_dn.callback = vol_dn_cb
        self.add_item(vol_dn)

        vol_up = discord.ui.Button(
            label="🔊 +", style=discord.ButtonStyle.secondary,
            custom_id=f"pvol_up_{self.user_id}", row=1)

        async def vol_up_cb(interaction):
            if interaction.user.id != self.user_id:
                try:
                    await interaction.response.send_message(
                        "Không phải player của bạn.", ephemeral=True)
                except Exception:
                    pass
                return
            try:
                st = mstate(self.guild.id)
                v = min(3.0, float(st.get("volume", 0.5)) + 0.1)
                st["volume"] = v
                vc = self.guild.voice_client
                if vc and vc.source and hasattr(vc.source, "volume"):
                    try:
                        vc.source.volume = v
                    except Exception:
                        pass
                await interaction.response.send_message(
                    f"🔊 Volume: `{int(v*100)}%`", ephemeral=True)
            except Exception as e:
                try:
                    await interaction.response.send_message(
                        f"❌ `{str(e)[:100]}`", ephemeral=True)
                except Exception:
                    pass

        vol_up.callback = vol_up_cb
        self.add_item(vol_up)

    async def play_track(self, interaction, track):
        guild = self.guild
        text_channel = self.text_channel
        member = interaction.user
        if not member.voice or not member.voice.channel:
            try:
                await interaction.followup.send(
                    "❌ Bạn phải vào voice trước.", ephemeral=True)
            except Exception:
                pass
            return
        target_channel = member.voice.channel
        vc = guild.voice_client
        try:
            if vc and vc.is_connected():
                if vc.channel != target_channel:
                    await vc.move_to(target_channel)
            else:
                vc = await target_channel.connect()
        except Exception as e:
            try:
                await interaction.followup.send(
                    f"❌ Không vào voice: `{str(e)[:100]}`", ephemeral=True)
            except Exception:
                pass
            return
        if vc.is_playing() or vc.is_paused():
            try:
                vc.stop()
            except Exception:
                pass
        _LyricsSender.cancel(guild.id)
        try:
            player = await YTDLSource.from_url(track["url"], stream=True)
        except Exception as e:
            try:
                await interaction.followup.send(
                    f"❌ Không phát được: `{str(e)[:150]}`", ephemeral=True)
            except Exception:
                pass
            return
        st = mstate(guild.id)
        st["current"] = track
        st["text_channel"] = text_channel.id
        st["loop_count"] = st["loop_max"] = 0
        try:
            player.volume = float(st.get("volume", 0.5))
        except Exception:
            pass

        # ✅ FIX v1.3
        captured_loop = self._loop
        _fired = {"done": False}

        def _after_playing(err):
            if _fired["done"]:
                return
            _fired["done"] = True
            if err:
                try:
                    _mp_log.error("player err: %s", err)
                except Exception:
                    pass
            try:
                if captured_loop and not captured_loop.is_closed() and captured_loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self._on_track_end(guild, vc, text_channel),
                        captured_loop)
            except Exception as e:
                try:
                    _mp_log.error("schedule _on_track_end: %s", e)
                except Exception:
                    pass

        if not vc.is_connected():
            try:
                await interaction.followup.send(
                    "❌ Voice bị ngắt kết nối.", ephemeral=True)
            except Exception:
                pass
            return
        try:
            vc.play(player, after=_after_playing)
        except Exception as e:
            try:
                await interaction.followup.send(
                    f"❌ Play fail: `{str(e)[:150]}`", ephemeral=True)
            except Exception:
                pass
            return

        dur_str = ""
        if track.get("duration"):
            try:
                m, s = divmod(int(track["duration"]), 60)
                dur_str = f"{m}:{s:02d}"
            except Exception:
                dur_str = "?"
        e = discord.Embed(
            title="🎶  ĐANG PHÁT",
            description=f"**{track.get('title', '?')[:200]}**",
            color=ROYAL_GOLD)
        if track.get("thumbnail"):
            e.set_thumbnail(url=track["thumbnail"])
        e.add_field(name="⏱️ Dài", value=dur_str or "?", inline=True)
        e.add_field(name="🎤 Yêu cầu",
                    value=str(track.get("requester", "?"))[:50], inline=True)
        try:
            vol = float(st.get("volume", 0.5))
        except Exception:
            vol = 0.5
        e.add_field(name="🔊 Volume",
                    value=f"`{int(vol * 100)}%`", inline=True)
        e.set_footer(text="Lyrics sẽ gửi tự động bên dưới ⬇️")
        try:
            await text_channel.send(embed=e)
        except Exception:
            pass
        asyncio.create_task(self._load_and_send_lyrics(
            track, text_channel, start_offset=0.5))

    async def _load_and_send_lyrics(self, track, text_channel, start_offset=0.0):
        try:
            title = track.get("title", "") or ""
            artist = track.get("uploader") or track.get("channel") or ""
            clean_title = title
            if " - " in title:
                parts = title.split(" - ", 1)
                artist_guess = parts[0].strip()
                title_guess = parts[1].strip()
                artist = artist_guess or artist
                clean_title = title_guess
            clean_title = re.sub(r"\(.*?\)|\[.*?\]", "", clean_title).strip()
            clean_title = re.sub(r"\s+(ft\.?|feat\.?|Featuring)\s+.*", "",
                                  clean_title, flags=re.I).strip()
            lyrics = await _fetch_lyrics(artist, clean_title,
                                          duration=track.get("duration"))
            if not lyrics:
                lyrics = await _fetch_lyrics("", title,
                                              duration=track.get("duration"))
            if not lyrics:
                try:
                    await text_channel.send("-# *Không tìm thấy lyrics.*")
                except Exception:
                    pass
                return
            synced = lyrics.get("synced", "")
            plain = lyrics.get("plain", "")
            if synced:
                lines = _parse_lrc(synced)
                if lines:
                    await _LyricsSender.start(
                        self.guild.id, text_channel, lines,
                        start_offset=start_offset)
                    return
            if plain:
                try:
                    await text_channel.send(
                        f"**📝 Lyrics — {lyrics.get('track', title)}**\n"
                        f"-# *(plain — không có timestamp)*")
                except Exception:
                    pass
                lines = plain.splitlines()
                chunks = [lines[i:i+4] for i in range(0, len(lines), 4)]
                for chunk in chunks[:30]:
                    text = "\n".join(l for l in chunk if l.strip())
                    if text.strip():
                        try:
                            await text_channel.send(f"-# {text}")
                        except Exception:
                            break
                        await asyncio.sleep(8)
            else:
                try:
                    await text_channel.send("-# *Không có lyrics.*")
                except Exception:
                    pass
        except Exception as e:
            try:
                await text_channel.send(f"-# *Lỗi lyrics: {str(e)[:80]}*")
            except Exception:
                pass

    async def _on_track_end(self, guild, vc, text_channel):
        """✅ FIX v1.3"""
        _LyricsSender.cancel(guild.id)
        captured_loop = self._loop
        if captured_loop is None or captured_loop.is_closed():
            try:
                captured_loop = asyncio.get_running_loop()
            except RuntimeError:
                captured_loop = None
        try:
            st = mstate(guild.id)
        except Exception:
            return
        if not vc or not vc.is_connected():
            try:
                st["current"] = None
            except Exception:
                pass
            return
        try:
            if st.get("queue"):
                next_track = st["queue"].pop(0)
                st["current"] = next_track
                try:
                    player = await YTDLSource.from_url(next_track["url"], stream=True)
                except Exception as e:
                    try:
                        _mp_log.error("extract next fail: %s", e)
                    except Exception:
                        pass
                    st["current"] = None
                    asyncio.create_task(self._on_track_end(guild, vc, text_channel))
                    return
                try:
                    player.volume = float(st.get("volume", 0.5))
                except Exception:
                    pass

                _fired2 = {"done": False}

                def _after_next(err):
                    if _fired2["done"]:
                        return
                    _fired2["done"] = True
                    if err:
                        try:
                            _mp_log.error("player err: %s", err)
                        except Exception:
                            pass
                    try:
                        if captured_loop and not captured_loop.is_closed() and captured_loop.is_running():
                            asyncio.run_coroutine_threadsafe(
                                self._on_track_end(guild, vc, text_channel),
                                captured_loop)
                    except Exception as e:
                        try:
                            _mp_log.error("schedule next: %s", e)
                        except Exception:
                            pass

                if not vc.is_connected():
                    st["current"] = None
                    return
                try:
                    vc.play(player, after=_after_next)
                except Exception as e:
                    try:
                        _mp_log.error("vc.play next fail: %s", e)
                    except Exception:
                        pass
                    st["current"] = None
                    return
                try:
                    e = discord.Embed(
                        title="🎶  ĐANG PHÁT",
                        description=f"**{next_track.get('title', '?')[:200]}**",
                        color=ROYAL_GOLD)
                    if next_track.get("thumbnail"):
                        e.set_thumbnail(url=next_track["thumbnail"])
                    await text_channel.send(embed=e)
                except Exception:
                    pass
                try:
                    asyncio.create_task(self._load_and_send_lyrics(
                        next_track, text_channel, 0.5))
                except Exception:
                    pass
            else:
                st["current"] = None
                await asyncio.sleep(30)
                if vc and vc.is_connected() and not vc.is_playing():
                    try:
                        await vc.disconnect()
                    except Exception:
                        pass
        except Exception as e:
            try:
                _mp_log.error("_on_track_end: %s", e)
            except Exception:
                pass


# ============================================================
# COMMANDS
# ============================================================
def _register_music_player_commands():
    global _MP_REGISTERED
    if _MP_REGISTERED:
        return
    _MP_REGISTERED = True

    @bot.command(name="player", aliases=["mp", "musicplayer"])
    async def cmd_player(ctx, *, query: str = None):
        if not is_allowed(ctx.author):
            await ctx.reply(pick_perm_insult())
            return
        if not ctx.guild:
            await ctx.reply("Chỉ dùng trong server.")
            return
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("🎧 Vào voice trước.")
            return
        tracks = []
        if query:
            queries = [q.strip() for q in query.split(",") if q.strip()][:10]
            if not queries:
                await ctx.reply("Query rỗng.")
                return
            msg = await ctx.send(f"🔍 Đang tìm `{len(queries)}` bài...")
            loop = asyncio.get_running_loop()
            for q in queries:
                try:
                    is_url = q.startswith("http")
                    info = await loop.run_in_executor(
                        executor,
                        lambda qq=q, uu=is_url: track_info(qq, uu))
                    if info:
                        tracks.append({**info, "requester": ctx.author.display_name})
                except Exception:
                    continue
            try:
                await msg.delete()
            except Exception:
                pass
            if not tracks:
                await ctx.reply("❌ Không tìm được bài nào.")
                return
        else:
            st = mstate(ctx.guild.id)
            for t in st.get("queue", [])[:25]:
                tracks.append(t)
            cur = st.get("current")
            if cur:
                tracks.insert(0, cur)
            if not tracks:
                await ctx.reply(
                    "**MUSIC PLAYER**\n"
                    "`!player` — mở player (dùng queue hiện tại)\n"
                    "`!player <bài 1>, <bài 2>, ...` — tìm + mở player\n\n"
                    "*Ví dụ:* `!player Sơn Tùng, Đen Vâu, Rap Việt`")
                return
        view = PlayerView(bot, ctx.guild, ctx.channel, tracks, ctx.author.id)
        e = discord.Embed(
            title="🎵  MUSIC PLAYER",
            description=(f"Chọn 1 bài từ dropdown để phát.\n"
                         f"Lyrics sẽ được gửi tự động từng dòng.\n\n"
                         f"**Tổng số bài:** `{len(tracks)}`"),
            color=0x5865F2)
        preview_lines = []
        for i, t in enumerate(tracks[:10], 1):
            dur = t.get("duration", 0)
            dur_str = ""
            if dur:
                try:
                    m, s = divmod(int(dur), 60)
                    dur_str = f" `{m}:{s:02d}`"
                except Exception:
                    pass
            preview_lines.append(f"`{i}.` {(t.get('title') or '?')[:70]}{dur_str}")
        if preview_lines:
            e.add_field(name="📋 Danh sách",
                         value="\n".join(preview_lines)[:1000], inline=False)
        e.set_footer(text=f"Player của {ctx.author.display_name}")
        if tracks[0].get("thumbnail"):
            e.set_thumbnail(url=tracks[0]["thumbnail"])
        try:
            await ctx.send(embed=e, view=view)
        except Exception as ex:
            try:
                await ctx.reply(f"❌ Gửi player lỗi: `{str(ex)[:150]}`")
            except Exception:
                pass

    @bot.command(name="lyrics", aliases=["loi", "loibaihat"])
    async def cmd_lyrics(ctx, *, query: str = None):
        if not is_allowed(ctx.author):
            await ctx.reply(pick_perm_insult())
            return
        if not query:
            st = mstate(ctx.guild.id)
            cur = st.get("current")
            if not cur:
                await ctx.reply("Dùng: `!lyrics <tên bài>` hoặc phát nhạc trước.")
                return
            query = cur.get("title", "")
            duration = cur.get("duration", 0)
        else:
            duration = None
        async with ctx.typing():
            artist = ""
            title = query
            if " - " in query:
                parts = query.split(" - ", 1)
                artist = parts[0].strip()
                title = parts[1].strip()
            title = re.sub(r"\(.*?\)|\[.*?\]", "", title).strip()
            lyrics = await _fetch_lyrics(artist, title, duration=duration)
            if not lyrics:
                lyrics = await _fetch_lyrics("", query, duration=duration)
            if not lyrics:
                await ctx.reply(f"❌ Không tìm thấy lyrics cho `{query[:80]}`.")
                return
            synced = lyrics.get("synced", "")
            plain = lyrics.get("plain", "")
            e = discord.Embed(
                title=f"📝  {lyrics.get('track', query)[:100]}",
                description=f"*{lyrics.get('artist', artist)[:100]}*",
                color=ROYAL_GOLD)
            e.set_footer(text=f"Nguồn: {lyrics.get('source', '?')}")
            if synced:
                lines = _parse_lrc(synced)
                preview = "\n".join(
                    f"`[{int(ts//60):02d}:{int(ts%60):02d}]` {txt}"
                    for ts, txt in lines[:25])
                e.add_field(name=f"🎬 Synced ({len(lines)} dòng)",
                             value=preview[:1500] or "—", inline=False)
                try:
                    await ctx.send(embed=e)
                except Exception:
                    pass
                return
            if plain:
                fb = io.BytesIO(plain.encode("utf-8"))
                try:
                    await ctx.send(embed=e,
                                    file=discord.File(
                                        fb, filename=f"lyrics_{title[:30]}.txt"))
                except Exception:
                    pass
                finally:
                    fb.close()
            else:
                await ctx.reply("❌ Lyrics rỗng.")


# ============================================================
# AUTO-SETUP
# ============================================================
_MP_REGISTERED = False

try:
    _register_music_player_commands()
    try:
        log.info("music_player.py v1.3 — commands registered")
    except Exception:
        pass
except Exception as _e:
    try:
        log.error("music_player.py setup FAILED: %s", _e)
    except Exception:
        print(f"music_player.py setup FAILED: {_e}")
    import traceback
    traceback.print_exc()