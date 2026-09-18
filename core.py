# core.py — PART 2: Roast + Fake + Human + Mirror + AFK + Stats + AutoDel (v7.2)
# + AUTO JOB TRACKING (live status cho autochui/autofake/spam/spamtin) — BÁ VƯƠNG EDITION
# ✅ FIX v7.2: Stats guard, cleanup task, memory leak fix

_R = random
_custom_roasts = []

# ============================================================
# STATS TRACKING
# ============================================================
_op_stats = {}
_stats_lock = threading.Lock()


def _stat_init(gid, kind, **info):
    with _stats_lock:
        _op_stats.setdefault(gid, {})[kind] = {
            "sent": 0, "failed": 0,
            "started": time.time(), "ended": None,
            "last_sent": 0, **info,
        }


def _stat_inc(gid, kind, ok=True):
    with _stats_lock:
        s = _op_stats.get(gid, {}).get(kind)
        if not s:
            return
        if ok:
            s["sent"] += 1
            s["last_sent"] = time.time()
        else:
            s["failed"] += 1


def _stat_end(gid, kind):
    with _stats_lock:
        s = _op_stats.get(gid, {}).get(kind)
        if s and s.get("ended") is None:
            s["ended"] = time.time()


def _stat_get(gid, kind=None):
    with _stats_lock:
        if kind:
            return dict(_op_stats.get(gid, {}).get(kind) or {})
        return {k: dict(v) for k, v in (_op_stats.get(gid) or {}).items()}


def _stat_cleanup():
    """✅ FIX: Xoá stats cũ hơn 24h để tránh memory leak."""
    now = time.time()
    with _stats_lock:
        for gid in list(_op_stats.keys()):
            for kind in list(_op_stats[gid].keys()):
                s = _op_stats[gid][kind]
                if s.get("ended") and now - s["ended"] > 86400:
                    _op_stats[gid].pop(kind, None)
            if not _op_stats[gid]:
                _op_stats.pop(gid, None)


# ============================================================
# AUTO JOB TRACKING — LIVE STATUS CHO AUTO-CHỬI/FAKE/SPAM
# ============================================================
_auto_jobs = {}          # {gid: {job_kind: AutoJob}}
_auto_job_lock = threading.Lock()


class AutoJob:
    """Job cho autochui / autofake / spam / spamtin — có live update."""
    def __init__(self, kind, guild_id, channel_id, target_id, target_name,
                 interval, **extra):
        self.kind = kind
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.target_id = target_id
        self.target_name = target_name or "?"
        self.interval = interval
        self.extra = extra
        self.started_at = time.time()
        self.ended_at = None
        self.sent = 0
        self.failed = 0
        self.last_sent = 0
        self.message_id = None
        self.status = "running"
        self.last_update = time.time()
        self._lock = threading.Lock()

    def inc(self, ok=True):
        with self._lock:
            if ok:
                self.sent += 1
                self.last_sent = time.time()
            else:
                self.failed += 1

    def finish(self, status="done"):
        with self._lock:
            self.status = status
            self.ended_at = time.time()


def _auto_job_get(gid, kind):
    with _auto_job_lock:
        return _auto_jobs.get(gid, {}).get(kind)


def _auto_job_set(job):
    with _auto_job_lock:
        _auto_jobs.setdefault(job.guild_id, {})[job.kind] = job


def _auto_job_del(gid, kind):
    with _auto_job_lock:
        g = _auto_jobs.get(gid)
        if g:
            g.pop(kind, None)
            if not g:
                _auto_jobs.pop(gid, None)


def _auto_job_all():
    with _auto_job_lock:
        out = []
        for gid, kinds in _auto_jobs.items():
            for kind, job in kinds.items():
                out.append(job)
        return out


# Bảng ngôn từ bá vương theo loại job
_AUTO_KIND_META = {
    "roast": {
        "icon": "⚔️",
        "label": "BỐ KHAI ĐAO",
        "sub": "CUỘC THẢM SÁT NGÔN TỪ",
        "color": ROYAL_RED,
        "verb": "chửi",
        "shell": "🌋 ĐẠN CHỬI",
        "shell_done": "quả đạn thần hồn",
        "shell_fail": "phát đạn cùi bắp",
        "stop_hint": "!stopchui",
        "target_title": "🎯 CON MỒI",
    },
    "fake": {
        "icon": "🎭",
        "label": "GIẢ DANH TÁC QUÁI",
        "sub": "MƯỢN MẶT GIE OAN",
        "color": ROYAL_RED,
        "verb": "fake",
        "shell": "🎭 MẶT NẠ",
        "shell_done": "màn kịch trót lọt",
        "shell_fail": "màn kịch đổ vỡ",
        "stop_hint": "!stopfake",
        "target_title": "🎯 KẺ BỊ GIE OAN",
    },
    "spam": {
        "icon": "💥",
        "label": "BÃO TIN HỦY DIỆT",
        "sub": "MƯA BOM KHÔNG NGỚT",
        "color": 0xFF5500,
        "verb": "bắn",
        "shell": "💥 BOM TIN",
        "shell_done": "quả bom nổ tung",
        "shell_fail": "quả bom xịt",
        "stop_hint": "!stopspam",
        "target_title": "🎯 MỤC TIÊU OANH TẠC",
    },
    "spamtin": {
        "icon": "📮",
        "label": "BÃO TIN ĐỊNH MỆNH",
        "sub": "TỪNG CON CHỮ NHƯ ĐAO PHỦ",
        "color": 0xFF8800,
        "verb": "gửi",
        "shell": "📮 TIN NHẮN",
        "shell_done": "tin nhắn tử thần",
        "shell_fail": "tin nhắn rơi vực",
        "stop_hint": "!stopspamtin",
        "target_title": "🎯 KẺ THỌ TIN",
    },
}

_STATUS_META = {
    "running":   {"icon": "🔥", "text": "ĐANG TÀN SÁT"},
    "done":      {"icon": "🏆", "text": "ĐÃ THU BINH"},
    "cancelled": {"icon": "🚫", "text": "ĐÃ RÚT QUÂN"},
}


def _bar(pct, length=18):
    pct = max(0, min(100, int(pct)))
    filled = int(length * pct / 100)
    return "█" * filled + "░" * (length - filled)


def _auto_job_embed(job):
    meta = _AUTO_KIND_META.get(job.kind, {
        "icon": "❔", "label": job.kind.upper(), "sub": "", "color": ROYAL_GOLD,
        "verb": "làm", "shell": "VIÊN ĐẠN", "shell_done": "viên đạn",
        "shell_fail": "viên đạn xịt", "stop_hint": "!stopall",
        "target_title": "🎯 MỤC TIÊU",
    })
    st = _STATUS_META.get(job.status, {"icon": "❔", "text": "KHÔNG RÕ"})

    now = time.time()
    end = job.ended_at or now
    dur = int(end - job.started_at)
    total_hits = job.sent + job.failed
    rate = round(job.sent / dur * 60, 1) if dur > 0 else 0.0
    accuracy = round(job.sent / total_hits * 100, 1) if total_hits else 100.0

    header = {
        "roast":   f"⚔️  **BỐ KHAI ĐAO** — Trẫm đang rót từng giọt cứt vào mặt thằng `<@{job.target_id}>`",
        "fake":    f"🎭  **GIẢ DANH TÁC QUÁI** — Trẫm mượn mặt `<@{job.target_id}>` đi gie oan khắp xứ",
        "spam":    f"💥  **BÃO TIN HỦY DIỆT** — Trẫm đang dội bom vào mặt `<@{job.target_id}>`",
        "spamtin": f"📮  **BÃO TIN ĐỊNH MỆNH** — Trẫm đang bắn từng con chữ như dao phủ vào `<@{job.target_id}>`",
    }.get(job.kind, f"{meta['icon']}  **{meta['label']}** — Trẫm đang ra tay")

    if job.status == "done":
        header = header.replace("đang", "đã")
    elif job.status == "cancelled":
        header = f"🚫  **{meta['label']}** — Trẫm đã thu đao, tha cho con chó `<@{job.target_id}>`"

    e = discord.Embed(
        title=f"{st['icon']}  {meta['icon']}  {meta['label']}  {meta['icon']}  {st['icon']}",
        description=f"{header}\n-# *{meta['sub']}* — Trạng thái: **{st['text']}**",
        color=meta["color"],
        timestamp=discord.utils.utcnow())

    e.add_field(
        name=meta["target_title"],
        value=f"<@{job.target_id}>\n`{job.target_name[:32]}`",
        inline=True)
    e.add_field(
        name="📍 Chiến trường",
        value=f"<#{job.channel_id}>",
        inline=True)
    e.add_field(
        name="⏲️ Nhịp rót đạn",
        value=f"`{job.interval:.2f}s`/phát",
        inline=True)

    if job.kind == "spamtin":
        total = job.extra.get("total", 0)
        pct = min(100, int(job.sent / max(total, 1) * 100)) if total else 0
        e.add_field(
            name=f"📡 TÀN SÁT ĐƯỢC — {pct}%",
            value=f"`{_bar(pct, 20)}`\n**`{job.sent}`** / `{total}` con chữ đã bắn vào mặt nó",
            inline=False)

    e.add_field(
        name=f"{meta['shell']} ĐÃ BẮN",
        value=f"**`{job.sent}`** {meta['shell_done']}",
        inline=True)
    e.add_field(
        name="💀 XỊT",
        value=f"`{job.failed}` {meta['shell_fail']}",
        inline=True)
    e.add_field(
        name="🎯 CHÍNH XÁC",
        value=f"`{accuracy}%`",
        inline=True)

    e.add_field(
        name="⏱️ TRẪM ĐÃ HÀNH HẠ",
        value=f"`{dur}s`",
        inline=True)
    e.add_field(
        name="⚡ TỐC ĐỘ",
        value=f"`{rate}/phút`",
        inline=True)
    e.add_field(
        name="🏆 ĐẲNG CẤP",
        value=f"`{_rank(dur, job.sent)}`",
        inline=True)

    if job.last_sent:
        gap = int(now - job.last_sent)
        e.add_field(
            name="🕐 PHÁT ĐẠN CUỐI",
            value=f"`{gap}s` trước",
            inline=True)

    if job.kind == "spam":
        e.add_field(
            name="💥 MỖI ĐỢT BẮN",
            value=f"`{job.extra.get('burst', '?')}` quả bom",
            inline=True)

    footers = {
        "roast":   f"⚔️ Gõ {meta['stop_hint']} để Trẫm thu đao — không tha mạng cho loại sâu bọ",
        "fake":    f"🎭 Gõ {meta['stop_hint']} để Trẫm tháo mặt nạ",
        "spam":    f"💥 Gõ {meta['stop_hint']} để Trẫm ngừng ném bom",
        "spamtin": f"📮 Gõ {meta['stop_hint']} để Trẫm ngừng rót chữ",
    }
    e.set_footer(text=footers.get(job.kind, f"Gõ !stopall để Trẫm thu binh"))

    return e


def _rank(dur, sent):
    """Xếp hạng mức độ bá đạo."""
    if sent >= 500:
        return "👑 ĐẾ VƯƠNG TÀN SÁT"
    if sent >= 200:
        return "⚔️ ĐẠI TƯỚNG KHAI ĐAO"
    if sent >= 100:
        return "🔥 CHIẾN THẦN"
    if sent >= 50:
        return "💀 SÁT THỦ"
    if sent >= 20:
        return "🥷 THỢ SĂN"
    if sent >= 5:
        return "🐺 CHÓ HOANG"
    return "🐣 TẬP SỰ"


async def _auto_job_update(job, force=False):
    """Update embed mỗi 3s."""
    now = time.time()
    if not force and now - job.last_update < 3:
        return
    job.last_update = now
    if not job.message_id:
        return
    try:
        ch = bot.get_channel(job.channel_id)
        if not ch:
            return
        msg = await ch.fetch_message(job.message_id)
        await msg.edit(embed=_auto_job_embed(job))
    except (discord.NotFound, discord.Forbidden):
        pass
    except Exception:
        pass


async def _auto_job_refresh_loop(job, max_ticks=3600):
    """Vòng lặp refresh embed mỗi 3s cho tới khi job kết thúc."""
    for _ in range(max_ticks):
        await asyncio.sleep(3)
        if job.status != "running":
            break
        await _auto_job_update(job)


@bot.command(name="ajob", aliases=["autojob", "ajobs", "autojobs", "jobauto"])
async def cmd_ajobs(ctx):
    """Xem tất cả auto jobs đang chạy."""
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return

    jobs = _auto_job_all()
    if ctx.guild:
        jobs = [j for j in jobs if j.guild_id == ctx.guild.id]

    if not jobs:
        await ctx.reply(
            "## 👑 **TRẪM KHÔNG CÓ CHIẾN DỊCH NÀO**\n"
            "Đang ngồi không, đéo có gì để tàn sát.\n\n"
            "**Muốn khơi mào?** Gõ:\n"
            "⚔️ `!autochui @user [giây]` — rót cứt liên tục\n"
            "🎭 `!autofake @user [giây]` — mượn mặt gie oan\n"
            "💥 `!spam @user [tin] [giây]` — thả bom từng đợt\n"
            "📮 `!spamtin @user <số> <giây> <text>` — bắn chữ vào mặt nó\n\n"
            "*Trẫm đang chờ khanh mở chiến dịch.*")
        return

    running = sum(1 for j in jobs if j.status == "running")
    e = discord.Embed(
        title="⚙️  BÀN THỜ CHIẾN DỊCH CỦA TRẪM  ⚙️",
        description=(f"**Trẫm đang theo dõi `{len(jobs)}` mặt trận** "
                     f"— trong đó **`{running}`** chiến dịch đang nổ ra.\n"
                     f"-# Mọi hành động của Trẫm đều khắc vào sử sách."),
        color=ROYAL_RED,
        timestamp=discord.utils.utcnow())

    for j in sorted(jobs, key=lambda x: x.started_at, reverse=True)[:10]:
        meta = _AUTO_KIND_META.get(j.kind, {
            "icon": "❔", "label": j.kind.upper(), "verb": "làm",
            "color": ROYAL_GOLD, "shell": "VIÊN ĐẠN",
        })
        st = _STATUS_META.get(j.status, {"icon": "❔", "text": "?"})
        dur = int((j.ended_at or time.time()) - j.started_at)
        rate = round(j.sent / dur * 60, 1) if dur > 0 else 0.0

        val = (
            f"**MỤC TIÊU:** <@{j.target_id}> · `{j.target_name[:22]}`\n"
            f"**{meta['shell']}:** `{j.sent}` · 💀 `{j.failed}` · "
            f"⚡ `{rate}/p` · ⏱️ `{dur}s`\n"
            f"**{meta['label']}** · {st['icon']} **{st['text']}**"
        )

        e.add_field(
            name=f"{meta['icon']} {st['icon']} `{j.kind.upper()}`",
            value=val,
            inline=False)

    e.set_footer(
        text="!stats → Bảng vàng chiến tích · "
             "!stopchui / !stopfake / !stopspam / !stopspamtin / !stopall")
    await ctx.send(embed=e)


_GENDER_F_WORDS = ["em", "chị", "cô", "dì", "thím", "bà", "mẹ", "má", "nữ", "nư",
    "girl", "female", "she", "her", "ms", "mrs", "miss", "lady", "queen",
    "princess", "chan", "san", "cute", "baby", "bé", "nhi", "linh",
    "mai", "lan", "hương", "thảo", "ngọc", "trang", "thư",
    "yến", "vy", "quỳnh", "như", "hà", "hân", "my", "mi", "miu",
    "kitty", "mèo", "cún", "bông", "sakura", "yuki", "hana", "mei"]

_GENDER_M_WORDS = ["anh", "chú", "bác", "ông", "ba", "bố", "cha", "nam", "trai",
    "boy", "male", "he", "him", "mr", "sir", "king", "prince",
    "kun", "bro", "dude", "guy", "man", "hùng", "dũng", "tuấn",
    "hoàng", "minh", "quân", "long", "sơn", "khánh", "phúc", "đức",
    "thắng", "thành", "tùng", "khoa", "kiệt", "lâm", "lộc", "nhân",
    "tiger", "dragon", "wolf", "hổ", "rồng", "sói", "gấu", "cọp"]


def detect_gender(user):
    try:
        uid = getattr(user, "id", user)
        row = db_run("SELECT gender FROM genders WHERE user_id=?", (int(uid),), one=True)
        if row and row[0] in ("nam", "nu", "neutral"):
            return row[0]
    except Exception:
        pass
    try:
        name = (getattr(user, "display_name", "") or getattr(user, "name", "") or "").lower()
    except Exception:
        name = ""
    if not name:
        return "neutral"
    for t in re.split(r"[\s_\-.|]+", name):
        if t in _GENDER_F_WORDS:
            return "nu"
        if t in _GENDER_M_WORDS:
            return "nam"
    for w in _GENDER_F_WORDS:
        if w in name:
            return "nu"
    for w in _GENDER_M_WORDS:
        if w in name:
            return "nam"
    return "neutral"


def set_gender_db(uid, gender):
    db_run("INSERT OR REPLACE INTO genders(user_id, gender) VALUES(?,?)", (int(uid), gender))


_ZW = ["\u200b", "\u200c", "\u200d", "\u2060"]


def _inject_zw(s, rate=0.15):
    if _R.random() > rate:
        return s
    out = []
    for ch in s:
        out.append(ch)
        if _R.random() < 0.04:
            out.append(_R.choice(_ZW))
    return "".join(out)


def _norm(s):
    return re.sub(r"[ \t]+", " ", s).strip()


_used_lines = deque(maxlen=5000)
_used_openers = deque(maxlen=1000)
_used_closers = deque(maxlen=1000)
_lock_line = threading.Lock()


def _line_key(s):
    s = re.sub(r"<@!?\d+>", "@", s)
    s = re.sub(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2700-\u27BF]", "", s)
    s = re.sub(r"[\u200b-\u200f\u2060]", "", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return hashlib.md5(s.encode("utf-8")).hexdigest()[:10]


def _pick_unique(pool, dq=None, max_try=50):
    if not pool:
        return None
    dq = dq if dq is not None else _used_lines
    with _lock_line:
        avail = [s for s in pool if _line_key(s) not in dq]
        if not avail:
            dq.clear()
            avail = list(pool)
        s = _R.choice(avail)
        dq.append(_line_key(s))
        return s


def _spread_mention(text, mention, chance=0.5):
    if "<@" in text or not mention:
        return text
    if _R.random() > chance:
        return text
    pos = _R.choices(["start", "end", "middle"], weights=[45, 40, 15], k=1)[0]
    if pos == "start":
        return f"{mention} {text}"
    if pos == "end":
        return f"{text} {mention}"
    words = text.split()
    if len(words) >= 3:
        idx = _R.randint(1, min(3, len(words) - 1))
        words.insert(idx, mention)
        return " ".join(words)
    return f"{mention} {text}"


_OPENERS_BASE = [
    "đm", "đmm", "đm mày", "đm con", "đm thằng", "đm cái loại", "đm cái thứ",
    "đm cái hạng", "đm cái đồ", "đm cái giống", "đm cái thứ chó má",
    "đụ má", "đụ mẹ", "đụ cụ", "đụ tổ", "đụ cả lò", "đụ ông bà",
    "địt cụ", "địt mẹ", "địt tổ", "địt cả dòng họ", "địt bà nội",
    "đjt mẹ", "đjt cụ", "đjt tổ tông",
    "vcl", "vl", "vc", "vkl", "vcl ra", "vãi cả lồn", "vãi cả cứt", "vãi cả đái",
    "clm", "clgt", "clmm", "clmn", "lz", "lol", "cặc", "lồn", "buồi", "đít", "cứt",
    "con cặc", "con lồn", "con buồi", "cái lồn", "cái cặc", "thằng lồn",
    "đm mày", "đm con mẹ mày", "đm ông già mày", "đm cả nhà mày",
    "đụ cả lò mày", "địt cụ tổ nhà mày", "đm dòng họ nhà mày",
    "đm 18 đời tổ tông mày", "đm con mẹ mày sinh ra mày",
    "nghe bố dạy này con", "bố nói cho mà nghe thằng lol",
    "ngồi im bố dạy", "câm mẹ mồm nghe bố nói",
    "mở mồm ra là bố ngửi thấy mùi cứt", "im mẹ mồm bố dạy cho",
    "bố đéo phải bạn mày, nghe bố nói", "nghe bố nói cấm cãi",
    "ai cho mày sủa khi bố đang nói", "bố đang nói mày im mẹ đi",
    "cút xa tầm nghe bố nói", "nghe bố dạy 1 lần thôi nhớ đời",
    "cấm mày ngắt lời bố", "mày tuổi lol gì mà mở mồm",
    "mày chưa đủ tuổi nói chuyện với bố", "mày tuổi cặc gì",
    "mày là cái đéo gì của bố",
    "phàm phu", "sâu bọ", "dân đen", "lũ kiến", "đồ con", "con giun",
    "rác rưởi", "rác thải", "phế vật", "súc vật", "súc sinh", "súc sanh",
    "óc chó", "óc bò", "óc dê", "óc lợn", "óc heo", "não bò",
    "đần độn", "ngu si", "đại ngu", "ngu ngốc", "ngu xuẩn", "ngu độn",
    "con chó", "thằng chó", "con chó hoang", "thằng chó đẻ",
    "con đbrr", "thằng đbrr", "cái loại đbrr", "cái hạng đbrr",
    "cái thứ", "thứ rác", "thứ bỏ đi", "loại súc vật", "loại chó má",
    "fuck you", "fuck your mom", "fuck your dad", "fuck your family",
    "stupid", "dumbass", "dumbfuck", "idiot", "moron", "imbecile",
    "dickhead", "asshole", "motherfucker", "cunt", "pussy",
    "son of a bitch", "piece of shit", "waste of oxygen", "worthless",
    "shut the fuck up", "stfu", "gtfo", "fuck off", "fuck u",
]

_OPENERS_GENDER = {
    "nam": ["đm thằng", "đm cái thằng", "thằng ranh con", "thằng lol",
        "thằng đbrr", "thằng loser", "thằng dumbass", "thằng súc vật",
        "thằng chó đẻ", "thằng đần độn", "thằng phế vật",
        "thằng yếu sinh lý", "thằng đàn bà", "thằng mặt lồn",
        "thằng nhát cáy", "thằng hèn hạ", "thằng đực rựa vô dụng",
        "đm cái thằng mặt cặc", "đm thằng chó hoang", "đm thằng ranh",
        "đm thằng lz", "đm thằng cặc", "đm cái thằng hèn",
        "thằng bất tài", "thằng vô dụng"],
    "nu": ["đm con", "đm cái con", "con ranh", "con lol",
        "con đbrr", "con bitch", "con loser", "con dẩm",
        "con mất dạy", "con đàn bà", "con ranh con", "con dẩm dớ",
        "con nhỏ nhà quê", "con đĩ", "con cặc", "con lồn",
        "con óc chó", "con phế vật", "con não ngắn",
        "đm con ranh con", "đm con đĩ", "đm con nhỏ hãm",
        "đm con đàn bà lắm mồm", "đm con già dẩm", "đm con mặt lồn",
        "con bất tài", "con vô dụng"],
    "neutral": ["đm cái loại", "đm cái hạng", "đm cái thứ", "đm cái đồ",
        "đồ vô dụng", "đồ bất tài", "đồ con hoang", "đồ rác rưởi",
        "đồ súc vật", "đồ phế vật", "đồ óc chó", "đồ đbrr",
        "cái loại đbrr", "cái hạng súc vật", "cái thứ rác rưởi"],
}

_BODY_LINES = [
    "mặt mày nhìn muốn đấm vào mồm 🤮", "cái mặt mày đéo khác gì đít nồi hun khói 💩",
    "mồm mày hôi như cống chảy ngược 3 ngày", "răng mày vàng như nghệ già, mở mồm ra là tỏa mùi cứt",
    "tóc mày rối như tổ quạ đêm bão giông", "mắt mày lồi như cá chết ngộp nước",
    "mũi mày tẹt như bánh đa vỡ, đéo khác gì con lợn 🐖", "da mày sần sùi như da cóc phơi nắng 40 độ",
    "mày gầy như que củi khô, đụng phát là gãy", "mày béo như heo nái sắp đẻ, bụng thõng tới đầu gối 🐖",
    "dáng mày như vịt bị bẻ chân, đi đứng lệch lạc 🦆", "mặt mày đầy mụn như cóc ghẻ, nhìn muốn ói 🐸",
    "mày xấu tới mức gương phải tự vỡ 🪞", "mày xấu tới mức bố mẹ mày cũng phải chạy trốn",
    "mặt mày như bị xe ben cán qua 3 lần", "nhìn mày 3 giây là bố mất ngủ 3 đêm",
    "mày xấu từ trong trứng xấu ra, gen của mày là gen lỗi", "nhan sắc mày là lỗi của tạo hóa ⚠️",
    "mặt mày như cái bánh bao chiều, nhúng nước còn đẹp hơn", "mày đứng cạnh ai cũng làm người ta xấu đi 50%",
    "mặt mày to như cái nia, đặt đâu che hết chỗ đó", "mồm mày rộng như mồm cống, ăn cả thế giới",
    "cái mồm mày to như mồm cống, nói câu nào xả cứt câu đó", "răng mày hô tới mức bố đéo dám nhìn thẳng",
    "răng mày vàng khè như bã trầu nhả ra, hôn cái nào sâu cái đó", "da mày đen như than tổ ong, đứng trong tối đéo thấy",
    "da mày ngăm ngăm như cá khô phơi 3 nắng, đen hơn đít nồi", "mắt mày lé tới mức nhìn 1 hướng được 2 hướng",
    "mắt mày híp như mắt lợn, nhìn đéo thấy gì", "mắt mày lồi như mắt ếch, nhìn phát sợ",
    "mũi mày to như cái cà rốt cắm giữa mặt", "mũi mày tẹt như bị đấm 10 lần, đéo còn sống mũi",
    "tai mày to như tai voi, nghe cái đéo gì", "tai mày vểnh như tai cún, nghe lén người khác",
    "mặt mày bóng như mỡ heo, đèn chiếu vào thấy phản chiếu", "mặt mày dầu như cái chảo chiên, lau mãi đéo sạch",
    "mày lùn như con kiến, đứng cạnh ai cũng tới rốn", "mày cao như cây sậy nhưng não như hạt cát",
    "mày cao như cột đình nhưng mặt như đít nồi", "tóc mày thưa như lông chuột",
    "tóc mày bết như mỡ chiên lâu ngày, đéo gội bao giờ", "mày hôi nách tới mức đứng cách 10m vẫn ngửi thấy",
    "mày hôi miệng tới mức nói câu nào nhặng câu đó", "mày hôi chân tới mức dép phải tự bỏ đi 🩴",
    "mày gầy như con mắm, gió thổi phát là bay", "mày béo như heo nái, mặc gì cũng chật",
    "mày béo phì tới mức cân nặng đéo có máy nào đo được", "mày gầy trơ xương, ai nhìn cũng tưởng HIV giai đoạn cuối",
    "da mày nhăn như da chó già, chưa 30 tuổi đã như 70", "mặt mày nhăn như khỉ ăn ớt, nhìn phát nản",
    "mày xấu tới mức AI tạo ảnh cũng từ chối vẽ", "mày xấu tới mức Photoshop cũng bó tay",
    "mày xấu tới mức mẹ đẻ ra cũng quay mặt", "mày xấu tới mức y tá đỡ đẻ phải xin lỗi",
    "mày xấu tới mức cái gương trong nhà mày tự đập đầu", "mày xấu tới mức Tinder phải ban acc vĩnh viễn",
    "mày xấu tới mức bác sĩ thẩm mỹ phải từ chối ca", "mày xấu tới mức camera an ninh phải xoay hướng khác",
    "não mày làm bằng bã đậu, đéo có tế bào nào 🧠", "mày ngu tới mức tường phải tự né 🧱",
    "IQ mày thua cả con giun đất đang bò", "IQ mày thua cả con kiến tha mồi",
    "IQ mày thua cả con chó nhà hàng xóm", "đầu mày chứa cứt hay chứa gì",
    "mày óc chó tới mức AI cũng phải bó tay 🤖", "não mày có chức năng gì không hay chỉ để đội nón",
    "mày ngu như bò mà bò còn khôn hơn mày 10 lần", "mày đần như chó gặp gương, sủa vào chính mình",
    "mày dốt tới tổ tiên phải quỳ xuống xin lỗi", "mày ngu tới Google cũng chịu thua",
    "mày ngố như bò đội nón 🐄", "mày ngu tới mức bố mẹ phải đi xét ADN",
    "mày nghĩ bằng đầu gối à", "não mày teo như bóng xì hơi",
    "óc mày như hạt đậu phộng, nhỏ mà rỗng", "não mày chạy 1% pin, mà pin còn bị chai 🔋",
    "mày đọc sách 10 năm vẫn dốt như bò đội nón", "mày học 20 năm vẫn ngu như con lợn chưa huấn luyện",
    "mày tiếp thu chậm như rùa già, chậm tới mức rùa bỏ đi", "đầu mày để trang trí à, đéo có gì trong đó",
    "não mày như tủ lạnh trống, mở ra không có gì", "mày ngu tới mức Google phải bó tay, AI phải chào thua",
    "não mày chắc nặng 3 gram, nhẹ hơn cả chim sẻ", "não mày mọc ở đít à, nói câu nào ngu câu đó",
    "mày đọc hiểu tiếng Việt còn đéo xong, nói chuyện với ai", "mày không biết đọc không biết viết, sống làm gì",
    "mày học lớp 1 rớt 3 lần, giờ tự hào à", "mày đéo qua nổi kỳ thi tốt nghiệp cấp 2",
    "mày dốt tới mức đéo có trường nào nhận", "mày dốt tới mức bố mẹ phải đút tiền cho trường",
    "mày dốt tới mức thầy cô phải từ chức", "mày ngu tới mức con chó nó cũng phải sủa cho tỉnh",
    "mày đéo có não, chỉ có 1 cục bã đậu trong đầu", "mày nghĩ 1 câu mất 10 tiếng, cả ngày đéo nghĩ được gì",
    "mày tự kỷ ám thị là mình khôn, thực ra ngu đéo ai bằng", "mày khôn nhà dại chợ, về nhà thì chó cũng đéo nghe",
    "mày khôn vặt, dại toàn tập, đéo ai thèm chơi", "mày bị khuyết tật não à, hay bẩm sinh đã ngu",
    "mày là sản phẩm lỗi của gen di truyền", "mày di truyền nguyên cái ngu từ bố mẹ",
    "mày thừa hưởng gen ngu của cả dòng họ", "mày nhận giải nobel về độ ngu chắc chắn top 1",
    "mày có thể đăng ký kỷ lục guinness về độ dốt", "mày ngu tới mức định nghĩa 'ngu' phải viết lại",
    "mày là bằng chứng sống của việc đéo cần não vẫn sống được", "não mày nhỏ hơn não chim cánh cụt, nhục đéo tả",
    "mày có IQ âm, đéo biết âm bao nhiêu", "mày cười 1 câu là người khác biết ngay mày đéo có não",
    "mày đéo có tí tự trọng nào 🤡", "mày đéo có chút liêm sỉ",
    "mày đéo có tí nhân cách", "mày là sai lầm của tạo hóa ⚠️",
    "mày là ô nhục của cả dòng họ", "mày là trò hề của cả server",
    "mày là demo lỗi của con người 🐛", "mày là định nghĩa sống của từ 'thất bại'",
    "mày là phế phẩm của xã hội 🗑️", "mày là súc vật đội lốt người",
    "mày hèn như con chó rách", "mày nhục như chó bị thiến",
    "mày đéo có tí giá trị", "mày đáng bị treo cổ 🪢",
    "mày là nỗi nhục của dòng tộc, tổ tiên mày phải khóc", "mày là nỗi nhục của gia đình, bố mẹ mày phải chuyển nhà",
    "mày sống làm ô nhục cả tổ tông 18 đời nhà mày", "mày là lỗi của hệ thống, đáng ra phải xóa từ lúc sinh",
    "mày còn đéo bằng con chó ngoài đường, chó còn biết sủa", "mày là nỗi ô nhục của giống nòi, đéo xứng làm người",
    "mày đéo xứng đáng có mặt trên đời", "mày sinh ra chỉ tổ làm nhục bố mẹ",
    "mày sống làm dơ cả nhân loại", "mày sống chỉ tổ tốn oxy 🫁",
    "mày thở cũng phí oxy", "mày đéo có ích gì cho đời",
    "mày là gánh nặng của xã hội 💸", "tương lai mày tối như đít nồi 🌑",
    "bố mẹ mày hối hận vì đã đẻ ra mày", "mày là cục nợ của gia đình",
    "mày đéo có tương lai đâu cưng", "mày sinh ra chỉ để làm trò cười 🤡",
    "mày sống lay lắt như ký sinh trùng 🦠", "mày là con số 0 tròn trĩnh 0️⃣",
    "mày là hố đen của trí tuệ 🕳️", "mày đéo bằng con kiến chăm chỉ",
    "mày là đống rác di động", "mày là nỗi thất vọng của nhân loại 😞",
    "mày phí 9 tháng 10 ngày của mẹ", "mày là sai lầm lớn nhất của vũ trụ",
    "mày là bug của dòng tộc 🐛", "mày là con sâu ghẻ của trái đất",
    "mày phí cả cuộc đời của bố mẹ mày", "mày tồn tại làm ô nhiễm không gian",
    "mày là con nợ của xã hội", "mày sống như con zombie biết đi",
    "mày sinh ra để làm bia đỡ đạn", "mày đéo đáng được ăn cơm",
    "mày đéo đáng được thở", "mày làm gì cũng hỏng, nói gì cũng sai",
    "mày sinh ra chỉ để người khác chửi", "mày là ví dụ sống cho câu 'đẻ ra thừa'",
    "mày là kết quả của việc uống rượu say khi đẻ", "mày là con của sai lầm, đéo phải con của tình yêu",
    "mày là đứa con hoang của xã hội", "mày đéo có bố, đéo có mẹ, chỉ có bàn phím",
    "mày là đứa rác rưởi của gia đình", "mày là hố đen của gia đình, hút hết tiền của bố mẹ",
    "mày là ung nhọt của xã hội", "mày là ký sinh trùng của nhân loại",
    "mày nói như vẹt học nói 🦜", "mày nói như bò rống 🐮",
    "mày mở miệng là tỏa mùi cứt 🤮", "mày càng nói càng lộ cái ngu",
    "mày nói chuyện như thiểu năng 🤪", "mày nói như đấm vào tai 👊",
    "mày sủa nhiều mà đéo có não 🐕", "mày nói nhảm như thần kinh",
    "mỗi câu mày nói là 1 lần tổ tiên xấu hổ", "mày càng gõ phím càng lộ mặt dốt",
    "mày nói chuyện như cái loa hỏng", "mày nói mà đéo ai thèm nghe",
    "mày mở mồm là bố biết não mày rỗng", "mày càng cãi càng chứng minh mày ngu",
    "mày nói tiếng người mà đéo ai hiểu", "mày gõ phím như trâu đạp chuột",
    "mày nói như đứa mất não", "mày nói chuyện như cái máy spam",
    "mày nói dài dòng như đàn bà", "mày nói dai như đỉa đói",
    "mày nói nhảm như bọn thất nghiệp", "mày nói câu nào là bố phải xoa tai câu đó",
    "mày nói như đang rặn ỉa, đéo ra được câu nào", "mày nói tiếng người đéo ai hiểu, nói tiếng chó chó cũng đéo hiểu",
    "mày nói nhiều nhưng đéo ai thèm nghe", "mày comment nhiều nhưng đéo có ai rep",
    "mày type 1000 chữ, đéo có 1 like", "mày post bài đéo ai thèm đọc",
    "mày viết dài nhưng đéo có 1 chút nội dung", "mày nói luyên thuyên như thầy bói",
    "mày nói nhảm như bà già hàng xóm", "mày nói chuyện như mấy đứa trẻ trâu",
    "mày nói như đang nói tiếng nước ngoài", "mày nói chuyện như cái loa phường",
    "mày nói năng vô duyên đéo ai muốn tiếp", "mày nói như đang đọc kinh, đéo có não",
    "mày nói sai chính tả đầy ra, đéo học lớp 1 à", "mày type sai chính tả liên tọi, đéo có văn hóa",
    "mày nói chuyện như con nít, đéo có chất người lớn", "mày nói câu nào là người khác muốn bịt tai",
    "mày như cứt trôi sông, tới đâu hôi đó 💩", "mày như cá thối bốc mùi cả xóm 🐟",
    "mày như gương vỡ méo mó 🪞", "mày như cây khô đéo ra quả 🌳",
    "mày như dơi mù bay loạn 🦇", "mày như xác chết biết đi 💀",
    "mày như giấy vệ sinh dùng xong vứt 🧻", "mày như cát sa mạc vô nghĩa 🏜️",
    "mày như laptop hết pin 🔋", "mày như đá ngăn đường 🪨",
    "mày như ruồi vo ve đéo ai đập 🪰", "mày như chó dại cắn bừa 🐕",
    "mày như cơm thiu ba ngày 🍚", "mày như bóng đèn đứt tóc 💡",
    "mày như bug của hệ thống vũ trụ", "mày như update lỗi của humanity",
    "mày như cơm nguội để lâu", "mày như bia hết ga",
    "mày như con sâu róm trong lỗ mũi", "mày như rác công nghiệp thải ra biển",
    "mày như cục đờm trong cổ họng", "mày như con ruồi bu quanh đĩa cứt",
    "mày như cục phân trôi sông", "mày như bãi nước cống mùa mưa",
    "mày như xác chuột trên đường", "mày như đống cứt khô ven đường",
    "mày như bao cao su dùng rồi", "mày như băng vệ sinh 3 ngày chưa thay",
    "mày như tã lót em bé chưa giặt", "mày như khăn lau nhà chưa phơi",
    "mày như con gián trong tủ bếp", "mày như con chuột cống hôi hám",
    "mày như con ve sầu kêu cả ngày", "mày như con sên bò mãi đéo tới",
    "mày như con ốc sên đéo có nhà", "mày như con cua bò ngang đéo ai ưa",
    "mày như con đỉa hút máu người ta", "mày như con rận trên đầu chó",
    "mày như con mối đục khoét xã hội", "mày như cái mụn cóc trên mặt đất",
    "bố mẹ mày sinh ra mày chắc chắn phải hối hận", "bố mẹ mày đẻ mày ra rồi có muốn bỏ không",
    "ông bà mày chắc phải khóc khi thấy mày lớn", "tổ tiên mày chắc phải chui từ dưới mộ lên xin lỗi",
    "dòng họ mày có mày là nỗi nhục lớn nhất", "mày làm ô nhục cả dòng họ 18 đời",
    "bố mẹ mày chắc nguyện đéo sinh mày ra", "ông bà mày chắc thất vọng tới mức đéo muốn nhìn mặt",
    "mày đéo xứng làm con của bố mẹ mày", "mày đéo xứng làm cháu của ông bà mày",
    "mày sinh ra làm cả gia đình phải chuyển nhà", "mày sinh ra làm cả dòng họ phải đổi tên",
    "bố mày chắc phải đi xét nghiệm lại ADN", "mẹ mày chắc phải đi khám tâm thần sau khi đẻ mày",
    "gia đình mày chắc phải ly tán vì có mày", "mày là cục nợ của cả dòng họ",
    "mày là tai họa của cả gia đình", "mày là ung nhọt của cả dòng tộc",
    "mày là vết nhơ của cả gia đình", "mày đéo có bố mẹ, chỉ có bàn phím làm bạn",
    "mày là đứa con hoang đéo ai nhận", "mày là kết quả của 1 đêm sai lầm",
    "mày là sản phẩm của 1 cuộc tình vụng trộm", "mày là hậu quả của việc uống rượu say đéo biết trời đất",
    "mày nghèo rớt mồng tơi, đéo có nổi 1 xu", "mày thất nghiệp dài hạn, ăn bám bố mẹ",
    "mày đéo có sự nghiệp, chỉ có bàn phím với mì tôm", "mày đéo có người yêu vì đéo ai thèm",
    "mày bị đá vì quá phế, đéo có tí tài cán", "mày cô đơn tới mức nói chuyện với tường",
    "mày đéo có bạn bè thật, chỉ có acc clone", "mày bị block khắp nơi, đéo ai muốn nhìn",
    "mày loser tới mức bố cũng phải thương hại", "mày đéo có gì trong tay ngoài cái ngu và cái dốt",
    "mày là nỗi nhục của cả cộng đồng mạng", "mày đéo đáng có internet, chỉ đáng ngồi trong chuồng",
    "mày là nỗi ô nhục của cả thế hệ", "mày sống đéo có tí ý nghĩa nào",
    "mày sống chỉ để làm nhục gia đình", "mày sống làm nhục bạn bè",
    "mày sống làm nhục cả xóm", "mày sống làm nhục cả đất nước",
    "mày sống làm nhục cả thế giới", "mày sinh ra là sai lầm của tạo hóa",
    "mày sinh ra là nỗi ô nhục của dòng họ", "mày sinh ra để làm trò cười thiên hạ",
    "mày sinh ra chỉ để làm mồi cho đời", "mày già đầu rồi mà vẫn ở nhà thuê",
    "mày đi làm 10 năm vẫn đéo có nổi 1 căn nhà", "mày đéo có sổ tiết kiệm, đéo có tương lai",
    "mày nợ nần chồng chất, đéo biết trả cách nào", "mày bị chủ nợ đuổi như chó đuổi",
    "mày bị bạn gái bỏ vì đéo có tiền", "mày bị vợ bỏ vì đéo có sức",
    "mày bị con cái bỏ vì đéo có tư cách", "mày bị bố mẹ đuổi khỏi nhà vì quá phế",
    "mày bị anh chị em xa lánh vì quá hèn", "mày bị họ hàng đéo thèm nhìn mặt",
    "mày bị làng xóm đéo thèm chào", "mày bị cả xã hội đéo thèm tiếp",
    "mày bị cả thế giới đéo thèm biết",
    "mày tuổi lol gì mà đòi lên mặt với bố", "bố mày đây, làm đéo gì được bố",
    "mày đéo có cửa với bố, đi cửa sau cũng đéo được", "bố gấp 10 lần mày về mọi thứ, kể cả ngu",
    "mày còn non lắm để bố dạy cho, đợi 20 năm nữa", "bố đang nói đéo ai cho mày ngắt lời",
    "mày làm đéo gì được bố, thử xem", "bố đây, con chó ạ, sủa tiếp đi",
    "mày là cháu bố, chào bố cái xem nào", "mày mới nứt mắt đã láo à con",
    "bố đéo phải bạn mày, im mẹ đi", "ai cho mày nói chuyện với bố như thế",
    "mày cầm tay bố mà xin lỗi", "bố vả cho phát giờ thì đéo biết mặt mũi",
    "mày tuổi trâu mà đòi sánh vai với bố", "bố mày từng đi tù, mày chỉ ở nhà nấu cơm",
    "bố giàu gấp vạn lần mày, mày chỉ là đứa ăn xin", "bố giỏi gấp trăm lần mày, mày chỉ là thằng rác",
    "bố nói câu nào mày phải nghe câu đó", "bố mày sinh ra mày mà mày còn cãi bố à",
    "bố mày thắp hương cho tổ tiên mày", "bố mày gặp mày ngoài đường là bố đá vào mồm",
    "bố đéo thèm đánh mày vì sợ bẩn tay", "mày là thứ đbrr đội lốt người, tắm 3 năm cũng đéo sạch",
    "mặt mày nhìn muốn đấm đéo chịu được", "não mày chắc làm bằng bã đậu đúng đéo",
    "đm mày sống làm gì cho tốn cơm", "mày nói 1 câu bố nghe 10 mùi cứt",
    "đm thằng lol không biết soi gương à", "mày là con chó cũng đéo xứng",
    "bố đéo hiểu sao mày tồn tại được", "mày là rác rưởi của xã hội",
    "đm mặt mày đéo ai muốn nhìn", "bố mày gặp mày ngoài đường là bố đái vào mặt",
    "cút về chuồng đi con vật 🐖", "mày là cái thứ chó má, đéo ai thèm đếm xỉa",
    "mày là cái loại cặn bã của xã hội", "mày là cái giống vô dụng, đéo làm được gì",
    "mày là cái thứ thừa thãi của vũ trụ", "mày là cái bãi rác di động của nhân loại",
]


_ATTACK_GENDER = {
    "nam": [
        "thằng đàn ông đéo ra gì, yếu như sên", "thằng yếu sinh lý, chưa làm gì đã mệt",
        "thằng hèn như đàn bà, gặp việc là chạy", "thằng nhát như thỏ đế, sợ cả bóng mình",
        "thằng đéo có trứng, đéo dám làm gì", "thằng ất ơ đầu đường xó chợ, đéo ai nhìn",
        "thằng con trai mà hèn hơn cả chó", "thằng mặt lol, đéo xứng làm đàn ông",
        "thằng đực rựa vô dụng, ăn rồi ngồi chơi", "thằng lz, đéo có tí tự trọng",
        "thằng dbrr, đứng đâu cũng bị đuổi", "thằng đéo có bản lĩnh, đéo dám đối mặt",
        "thằng hèn chó, đéo dám sủa ai", "thằng cặc, đéo bằng thằng đàn bà",
        "thằng cu, đéo làm được tích sự gì", "thằng già trâu mà đéo có tí khôn",
        "thằng trẻ trâu, mới lớn đã láo", "thằng nhóc con, tuổi đéo bằng bố mày",
        "thằng mặt mụn, đéo ai thèm nhìn", "thằng đàn ông mà để vợ nó đánh, nhục đéo tả",
        "thằng chồng mà đéo lo được cho vợ con", "thằng bố mà con nó cũng đéo thèm nhìn",
        "thằng con trai mà suốt ngày khóc lóc", "thằng đực rựa mà yếu sinh lý, đéo ai thèm",
        "thằng mặt cặc, đi đâu cũng bị chửi", "thằng đàn bà đội lốt đàn ông, nhục vcl",
        "thằng hèn nhát, sợ cả cái bóng của mình",
    ],
    "nu": [
        "con đàn bà lắm mồm, nói như phát thanh", "con già dẩm, đéo ai yêu",
        "con đéo ai thèm, tới giờ vẫn ế", "con ế chồng ế con, tới già vẫn cô đơn",
        "con nhỏ nhà quê, đéo có tí tinh tế", "con não ngắn như que tăm, nghĩ đéo ra gì",
        "con đàn bà dữ như chó cắn, gặp là muốn cắn", "con ranh con, mới lớn đã láo",
        "con dẩm dớ, làm gì cũng sến", "con mất dạy, bố mẹ dạy đéo đến nơi",
        "con lz, đéo có tí giá trị", "con dbrr, đứng đâu cũng bị chửi",
        "con đào mỏ, đéo có tí tự trọng", "con phá đòi, đéo ai cưới",
        "con điếm, bán rẻ cũng đéo ai mua", "con lồn, mở mồm ra là tỏa mùi cứt",
        "con cặc, đéo có tí liêm sỉ", "con đĩ, ai cho tiền là theo",
        "con bán thân, đéo có tí danh dự", "con mặt mụn, đéo ai muốn nhìn",
        "con dẩm, suốt ngày đăng story tự kỷ", "con ảo tưởng, nghĩ mình là hot girl",
        "con nhà quê lên phố, đéo biết cách ăn mặc", "con nghèo rớt, đéo có nổi bộ đồ tử tế",
        "con không chồng mà có con, đéo biết bố nó là ai", "con cô đơn tới mức lên mạng tìm bồ",
        "con bị đá 10 lần rồi vẫn ảo tưởng", "con bị người yêu bỏ vì quá dẩm",
    ],
    "neutral": [
        "đồ vô dụng, đéo làm được gì", "đồ bất tài, cầm cái gì cũng hỏng",
        "đồ con hoang, đéo có giáo dục", "đồ rác rưởi, đéo ai cần",
        "đồ súc vật, tắm 3 năm cũng đéo sạch", "đồ phế vật, ăn hại xã hội",
        "đồ óc chó, não như bã đậu", "đồ đbrr, không ai coi ra gì",
        "đồ cặn bã, đéo bằng cứt", "đồ hạ đẳng, sinh ra đã thấp kém",
        "đồ thừa thãi, sinh ra để làm gánh nặng", "đồ vô tích sự, đéo đóng góp gì cho đời",
        "đồ hèn hạ, sống nhục cả đời", "đồ đê tiện, làm gì cũng bẩn",
        "đồ rác, sống làm ô nhiễm không khí",
    ],
}


_CLOSERS_BASE = [
    "cút mẹ mày đi 🚪", "biến mẹ mày đi 💨", "cút xéo 💨", "biến thật xa 🌌",
    "next mẹ mày đi ⏭️", "cút khỏi mắt bố 👀", "biến đi cho bố nhờ",
    "cút cút cút 🚶", "đi chỗ khác mà sủa 🐕", "cút về chuồng 🐖",
    "im mẹ mồm lại 🤫", "câm mẹ mày đi", "ngậm mồm vào 🤐",
    "sủa ít thôi con 🐕", "bớt nói nhảm đi thằng lol", "ngừng sủa 🛑",
    "shut the fuck up 🐕", "stfu mẹ đi", "câm mẹ mồm không bố đánh",
    "im ngay và luôn", "tắt mẹ loa đi", "câm như thóc 🌾",
    "ngậm cứt vào mà ăn", "ngậm cặc mà mút", "ngậm lồn mà liếm",
    "về soi gương đi 🪞", "nhìn lại mình đi con", "tự thấy nhục chưa 🤡",
    "về ôm mẹ mà khóc 🤱", "về xin mẹ tiền mua não đi",
    "đi khám tâm thần đi con", "gọi 115 giùm mày",
    "về tự kỷ đi cho xã hội đỡ phiền",
    "off mẹ đi 📴", "log out mẹ đi", "shutdown mẹ đi 💻", "tắt điện 💡",
    "cook mẹ đi 🍳", "bớt ảo tưởng 🎭", "log out cả acc",
    "karma gõ cửa ⚡", "chờ báo ứng 🔮", "bố khinh 💀", "mày đéo xứng 🚫",
    "về với cống rãnh 🚰", "bye nhé đéo tiễn 👋", "đéo rảnh 🥱",
    "đéo ai hỏi mày ❓", "who the fuck asked 🤷",
    "cút xa tầm nhìn của bố", "đừng để bố phải nhắc lần 2",
    "im mồm ngay và luôn", "cút trước khi bố nóng",
    "về với tổ tiên mày đi ⚰️", "đi chết mẹ mày đi ☠️",
    "trẫm đéo rảnh tiếp mày", "mày đéo đáng để bố trả lời",
    "bố đéo nói lần 3 đâu đấy", "cút trước khi bố nổi điên",
    "về ăn cơm với mẹ đi 🍚", "đi ngủ sớm cho tỉnh 🛏️",
    "uống trà sữa cho bớt ngu 🧋", "đi ăn kem cho hạ hỏa 🍦",
    "thôi bố tha cho mày về", "đi chỗ khác chơi đi con",
    "cút mẹ mày đi cho bố nhờ", "biến mẹ mày đi cho bố nhờ",
    "về với cái máng lợn nhà mày đi", "về với chuồng lợn nhà mày",
    "về với đống rác nhà mày", "về với cống nhà mày",
    "tự sát mẹ mày đi cho sạch xã hội", "tự tử mẹ mày đi cho rồi",
    "đi chết mẹ mày đi cho đỡ tốn oxy", "chết mẹ mày đi cho đỡ tốn cơm",
    "về mà làm trò cho mẹ mày xem", "về mà sủa cho chó nó nghe",
    "thôi cút mẹ mày đi", "biến mẹ nó đi cho nhanh",
]

_EMOJI_POOL = ["", "", "", "", "", " 🤡", " 💀", " 🗑️", " 😂", " 💩",
               " ⚰️", " 🐕", " 🔥", " ☠️", " 🤮", " 🖕", " 🚪", " 🐖"]


def _emojis(n):
    return "".join(_R.choice(_EMOJI_POOL) for _ in range(n))


_AUTO_TIER = "huydiet"
_AUTO_ZW_INJECT = 0.55

_ROAST_TIER = {
    "nhe":    {"open": 0.5, "atk": 1, "close": 0.4, "emoji": 1},
    "vua":    {"open": 0.8, "atk": 2, "close": 0.7, "emoji": 1},
    "nang":   {"open": 1.0, "atk": 3, "close": 0.9, "emoji": 1},
    "huydiet":{"open": 1.0, "atk": 4, "close": 1.0, "emoji": 2},
}
_default_tier = "huydiet"


def forge_roast(target, tier=None, gender="neutral", inject_zw=True):
    if not target:
        target = "mày"
    target = str(target)[:80].strip() or "mày"
    tier = tier if tier in _ROAST_TIER else _default_tier
    cfg = _ROAST_TIER[tier]

    opener = ""
    if _R.random() < cfg["open"]:
        pool = _OPENERS_BASE + _OPENERS_GENDER.get(gender, [])
        opener = _pick_unique(pool, _used_openers)

    n_atk = _R.randint(1, min(2, cfg["atk"]))
    body_pool = _BODY_LINES + _ATTACK_GENDER.get(gender, [])
    bodies = []
    for _ in range(n_atk):
        b = _pick_unique(body_pool)
        if b and b not in bodies:
            bodies.append(b)
    body = ", ".join(bodies) if bodies else ""

    closer = ""
    if _R.random() < cfg["close"]:
        closer = _pick_unique(_CLOSERS_BASE, _used_closers)

    parts = [p for p in [opener, body, closer] if p]
    if not parts:
        parts = [f"đm {target} 🤡"]

    if len(parts) == 1:
        s = parts[0]
    elif len(parts) == 2:
        s = f"{parts[0]}, {parts[1]}"
    else:
        s = f"{parts[0]}, {parts[1]}. {parts[2]}"
    s = _norm(s + _emojis(cfg["emoji"]))

    if _R.random() < 0.75:
        s = _spread_mention(s, target, chance=1.0)
    else:
        if target not in s:
            s = f"{target} {s}"
    if inject_zw:
        s = _inject_zw(s, rate=0.4)
    return s


def forge_roast_combo(target, gender="neutral", lines=6):
    if not target:
        target = "mày"
    target = str(target)[:80].strip() or "mày"
    n = max(4, min(12, lines))
    out = []
    seen = set()

    def add(line, force_tag=False):
        k = _line_key(line)
        if k in seen:
            return False
        seen.add(k)
        if force_tag:
            line = f"{target} {line}" if target not in line else line
        else:
            line = _spread_mention(line, target, chance=0.45)
        line = _norm(line + _emojis(_R.randint(0, 1)))
        out.append(_inject_zw(line, rate=0.3))
        return True

    opener_pool = _OPENERS_BASE + _OPENERS_GENDER.get(gender, [])
    op = _pick_unique(opener_pool, _used_openers) or "đm"
    body_pool = _BODY_LINES + _ATTACK_GENDER.get(gender, [])
    fb = _pick_unique(body_pool)
    first = f"{op}, {fb}" if fb else f"{op}, não mày làm bằng cứt chó à"
    add(first, force_tag=True)

    tries = 0
    while len(out) < n - 1 and tries < 150:
        tries += 1
        b = _pick_unique(body_pool)
        if not b:
            break
        add(b, force_tag=False)

    cl = _pick_unique(_CLOSERS_BASE, _used_closers) or "cút mẹ mày đi 🚪"
    add(cl, force_tag=True)
    return "\n".join(out)


def forge_roast_mega(target, gender="neutral"):
    return forge_roast_combo(target, gender=gender, lines=_R.randint(7, 12))


def load_custom_roasts():
    global _custom_roasts
    try:
        rows = db_run("SELECT text FROM roast_custom", many=True) or []
        _custom_roasts = [r[0] for r in rows if r[0] and "{t}" in r[0]]
        log.info("Custom roast: %d", len(_custom_roasts))
    except Exception as e:
        log.error("load_custom_roasts: %s", e)
        _custom_roasts = []


_FAKE_1P_TEMPLATES = [
    "tao ngu quá các bạn ạ 😭", "đm tao, sao tao ngu thế này 💀",
    "tao ngu như con bò ăn cỏ 🐮", "não tao làm bằng bã đậu 🧠",
    "IQ tao thua con giun đất", "tao cần đi khám não gấp 🏥",
    "tao ngố như bò đội nón 🐄", "tao đần như chó gặp gương 🐕",
    "tao là thằng loser của server 🤡", "tao thua kém tất cả mọi người",
    "tao là con số 0 tròn trĩnh 0️⃣", "tao là hố đen của trí tuệ 🕳️",
    "tao là nỗi thất vọng của nhân loại 😞", "tao là thất bại cả thế hệ",
    "tao là sai lầm của tạo hóa ⚠️", "tao là phế phẩm của xã hội 🗑️",
    "tao đéo bằng con chó ngoài đường 🐕", "tao đéo bằng con kiến chăm chỉ",
    "tao vô dụng vcl các bạn ạ", "tao đéo có ích gì cho xã hội 🚫",
    "tao sống chỉ tổ tốn oxy 🫁", "tao thở cũng phí oxy",
    "tao là gánh nặng của xã hội 💸", "tao sinh ra chỉ tổ làm khổ bố mẹ",
    "tao xấu vcl các bạn ạ 😭", "tao xấu tới gương phải tự vỡ 🪞",
    "tao xấu tới bố mẹ cũng chạy", "mặt tao như đít nồi hun khói 💩",
    "tao hèn vcl các bạn ạ", "tao đéo có tí tự trọng nào 🤡",
    "tao đéo có chút liêm sỉ 🐕", "tao tự thấy bản thân nhục vcl 😔",
    "tao xin lỗi vì tồn tại", "tao biết mình là rác rưởi rồi",
    "tao chán sống quá các bạn ạ 😩", "tao thà đéo sinh ra còn hơn ⚰️",
    "tao đéo đáng sống các bạn ạ", "tao đéo có gì cả 😔",
    "tao đéo có tài cán gì", "tao đéo có tương lai gì",
    "tao có mỗi cái ngu là giỏi", "tao nghèo rớt mồng tơi",
    "tao thất nghiệp vcl", "tao đéo có người yêu vì quá loser",
    "tao ngu tới mức AI cũng bó tay 🤖", "tao ngu tới Google cũng chịu",
    "tao cô đơn vcl các bạn ạ 🥺", "tao cô đơn tới mức nói chuyện với tường",
    "tao bị tất cả mọi người xa lánh", "tao ngồi một mình cả ngày",
    "tao là sai lầm lớn nhất của vũ trụ",
]

_FAKE_1P_COMBO = [
    ["tao ngu quá các bạn ạ 😭", "não tao làm bằng bã đậu",
     "đéo hiểu sao tao tồn tại", "thôi tao cút"],
    ["đm tao, sao tao ngu vcl", "IQ tao thua con giun",
     "bố mẹ hối hận đẻ ra tao", "tao nên biến mất"],
    ["tao là thằng loser của server", "đéo có tí giá trị nào",
     "ai cũng ghét tao", "tao xin lỗi vì tồn tại 🙏"],
    ["tao xấu vcl các bạn ạ", "nhìn gương phát sợ",
     "bố mẹ cũng chạy mất", "tao nên đeo khẩu trang 24/7"],
    ["tao vô dụng vcl", "làm gì cũng hỏng", "nói gì cũng sai",
     "tao tự thấy nhục 😔"],
]

_FAKE_EMOJIS = ["", "", "", "", " 😭", " 🤡", " 💩", " 😔", " 🥲",
                " ⚰️", " 😂", " 🥺", " 🐕", " 🗑️", " 💀"]


def forge_fake():
    r = _R.random()
    if r < 0.20:
        n = _R.randint(3, 4)
        return "\n".join(_inject_zw(s, rate=0.4) for s in _R.sample(_FAKE_1P_TEMPLATES, n))
    if r < 0.35:
        return "\n".join(_inject_zw(s, rate=0.4) for s in _R.sample(_FAKE_1P_TEMPLATES, 5))
    if r < 0.50:
        return "\n".join(_inject_zw(s, rate=0.3) for s in _R.choice(_FAKE_1P_COMBO))
    s = _R.choice(_FAKE_1P_TEMPLATES)
    if _R.random() < 0.6:
        s += _R.choice(_FAKE_EMOJIS)
    return _inject_zw(s, rate=_AUTO_ZW_INJECT)


def _wh_save_pool(cid, pool):
    try:
        data = []
        for e in pool:
            wh = e.get("wh")
            if wh and hasattr(wh, "id"):
                data.append({"id": wh.id, "fails": e.get("fails", 0)})
        db_run("INSERT OR REPLACE INTO wh_pools(channel_id, data, updated_at) "
               "VALUES(?,?,?)",
               (cid, json.dumps(data), time.time()))
    except Exception:
        pass


def _wh_load_pool(cid):
    try:
        row = db_run("SELECT data FROM wh_pools WHERE channel_id=?", (cid,), one=True)
        if row and row[0]:
            return json.loads(row[0])
    except Exception:
        pass
    return []


async def _wh_restore(channel):
    saved = _wh_load_pool(channel.id)
    if not saved:
        return []
    pool = []
    try:
        whs = await channel.webhooks()
        by_id = {w.id: w for w in whs}
        for s in saved:
            wh = by_id.get(s["id"])
            if wh:
                pool.append({"wh": wh, "fails": s.get("fails", 0),
                             "last": 0, "created": time.time()})
    except Exception:
        pass
    return pool


async def _pool_get(channel):
    now = time.time()
    pool = _wh_pool.get(channel.id, [])
    pool = [e for e in pool if e["fails"] < 5 and now - e["created"] <= _POOL_TTL]
    try:
        me = channel.guild.me if hasattr(channel, "guild") else None
        if me:
            perms = channel.permissions_for(me)
            if not perms.manage_webhooks:
                _wh_pool[channel.id] = pool
                return pool
    except Exception:
        pass
    if len(pool) < _POOL_SIZE:
        try:
            for w in await channel.webhooks():
                if (w.name and w.name.startswith("BOT_FAKE")
                        and w.user and w.user.id == bot.user.id
                        and len(pool) < _POOL_SIZE):
                    pool.append({"wh": w, "fails": 0, "last": 0, "created": now})
        except Exception:
            pass
    need = _POOL_SIZE - len(pool)
    for i in range(min(need, 3)):
        try:
            wh = await channel.create_webhook(name=f"BOT_FAKE_{int(time.time())}_{i}")
            pool.append({"wh": wh, "fails": 0, "last": 0, "created": now})
        except Exception:
            break
    _wh_pool[channel.id] = pool
    try:
        _wh_save_pool(channel.id, pool)
    except Exception:
        pass
    return pool


def _pool_pick(pool):
    now = time.time()
    cands = [e for e in pool if now - e["last"] >= 1.5 and e["fails"] < 5]
    if not cands:
        cands = sorted(pool, key=lambda x: (x["fails"], x["last"]))[:1]
    if not cands:
        return None
    cands.sort(key=lambda x: (x["fails"], x["last"]))
    return cands[0]


async def _wh_wait(channel_id):
    now = time.time()
    last = _wh_last_send.get(channel_id, 0)
    gap = now - last
    if gap < _WH_MIN_GAP:
        jitter = _WH_MIN_GAP * (1 + random.uniform(-0.2, 0.2))
        await asyncio.sleep(max(0, jitter - gap))
    _wh_last_send[channel_id] = time.time()


async def fake_send(channel, target_member, content, retries=3):
    base = (target_member.display_name or target_member.name)[:20] or "user"
    pusher = "".join(_R.choice(["\u2800", "\u200b", "\u200c", "\u200d", "\u2060"])
                     for _ in range(_R.randint(3, 15)))
    name = f"{base}{pusher}"[:80]
    try:
        avatar = target_member.display_avatar.url
    except Exception:
        avatar = None
    content = _inject_zw(content, rate=0.5)
    await _wh_wait(channel.id)
    pool = await _pool_get(channel)
    if not pool:
        return await _fallback_send(channel, base, content)
    for _ in range(retries + 1):
        entry = _pool_pick(pool)
        if not entry:
            break
        try:
            await asyncio.sleep(_R.uniform(0.05, 0.3))
            await entry["wh"].send(
                content=content, username=name, avatar_url=avatar, wait=True,
                allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True))
            entry["fails"] = 0
            entry["last"] = time.time()
            _wh_last_send[channel.id] = time.time()
            return True
        except (discord.NotFound, discord.Forbidden):
            entry["fails"] = 999
            continue
        except discord.HTTPException as e:
            if e.status == 429:
                ra = getattr(e, "retry_after", 2.0) or 2.0
                entry["fails"] += 1
                await asyncio.sleep(min(ra * _R.uniform(1.0, 1.5), 8.0))
                continue
            entry["fails"] += 1
            continue
        except Exception:
            entry["fails"] += 1
            continue
    return await _fallback_send(channel, base, content)


async def _fallback_send(channel, base, content):
    try:
        await channel.send(f"**{base}**: {content}")
        return True
    except Exception:
        return False


def _parse_interval(s, default=1.5, lo=1.0, hi=60.0):
    if s is None:
        return default
    if isinstance(s, (int, float)):
        v = float(s)
    else:
        s = str(s).strip().rstrip("xs").replace(",", ".")
        try:
            v = float(s)
        except Exception:
            return default
    return max(lo, min(hi, v))


_HUMAN_ENABLED = {}


def _is_human_on(channel_id):
    return _HUMAN_ENABLED.get(channel_id, False)


async def send_as_human(channel, content, name=None, avatar=None, retries=2):
    if not content:
        return False
    name = name or HUMAN_NAME
    avatar = avatar or (HUMAN_AVATAR or None)
    content = str(content)[:2000]
    for _ in range(retries + 1):
        try:
            await _wh_wait(channel.id)
            pool = await _pool_get(channel)
            entry = _pool_pick(pool)
            if not entry:
                try:
                    await channel.send(content)
                    return True
                except Exception:
                    return False
            try:
                await entry["wh"].send(
                    content=content, username=name[:80], avatar_url=avatar, wait=True,
                    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True))
                entry["last"] = time.time()
                entry["fails"] = 0
                _wh_last_send[channel.id] = time.time()
                return True
            except (discord.NotFound, discord.Forbidden):
                entry["fails"] = 999
                continue
            except discord.HTTPException as e:
                if e.status == 429:
                    ra = getattr(e, "retry_after", 2.0) or 2.0
                    entry["fails"] += 1
                    await asyncio.sleep(min(ra * 1.2, 6.0))
                    continue
                entry["fails"] += 1
                continue
        except Exception:
            continue
    try:
        await channel.send(content)
        return True
    except Exception:
        return False


async def reply_as_human(msg, content):
    try:
        uid = msg.author.id
        if f"<@{uid}>" not in content and f"<@!{uid}>" not in content:
            text = f"<@{uid}> {content}"
        else:
            text = content
        return await send_as_human(msg.channel, text)
    except Exception:
        try:
            await msg.reply(content[:1900], mention_author=False)
            return True
        except Exception:
            return False


_MIRROR_ENABLED = {}
_MIRROR_DELETE_ORIG = True
_MIRROR_LOG = deque(maxlen=500)


@bot.command(name="mirror")
async def cmd_mirror(ctx, mode: str = None):
    global _MIRROR_DELETE_ORIG
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    cid = ctx.channel.id
    if mode in ("on", "bat", "bật", "1"):
        _MIRROR_ENABLED[cid] = True
        await ctx.reply("🎭 Mirror BẬT")
    elif mode in ("off", "tat", "tắt", "0"):
        _MIRROR_ENABLED[cid] = False
        await ctx.reply("🎭 Mirror TẮT")
    elif mode in ("del", "delete"):
        _MIRROR_DELETE_ORIG = not _MIRROR_DELETE_ORIG
        await ctx.reply(f"Xóa tin gốc: {'ON' if _MIRROR_DELETE_ORIG else 'OFF'}")
    else:
        cur = _MIRROR_ENABLED.get(cid, False)
        _MIRROR_ENABLED[cid] = not cur
        await ctx.reply(f"🎭 Mirror {'BẬT' if not cur else 'TẮT'}")


@bot.listen("on_message")
async def _mirror_listener(msg):
    if msg.author.bot or not msg.guild or msg.webhook_id:
        return
    if msg.content.startswith("!"):
        return
    cid = msg.channel.id
    if not _MIRROR_ENABLED.get(cid, False):
        return
    try:
        me = msg.guild.me
        perms = msg.channel.permissions_for(me)
        if not perms.manage_webhooks:
            return
        content = msg.content
        author_name = msg.author.display_name
        author_avatar = msg.author.display_avatar.url
        attachments_url = [a.url for a in msg.attachments]
        files = []
        for url in attachments_url[:3]:
            try:
                s = await http()
                async with s.get(url, timeout=15) as r:
                    if r.status == 200:
                        data = await r.read()
                        if len(data) < 8 * 1024 * 1024:
                            fname = url.split("/")[-1].split("?")[0] or f"file_{len(files)}"
                            files.append(discord.File(io.BytesIO(data), filename=fname))
            except Exception:
                continue
        if not content and not files:
            return
        pool = await _pool_get(msg.channel)
        entry = _pool_pick(pool)
        if not entry:
            return
        try:
            sent = await entry["wh"].send(
                content=content[:2000] or None,
                username=author_name[:80], avatar_url=author_avatar,
                files=files if files else discord.utils.MISSING, wait=True,
                allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True))
            entry["last"] = time.time()
            entry["fails"] = 0
        except Exception:
            return
        _MIRROR_LOG.append({"ch": cid, "author": author_name, "avatar": author_avatar,
                             "content": content[:500], "attachments": attachments_url,
                             "ts": time.time()})
        if _MIRROR_DELETE_ORIG and perms.manage_messages:
            try:
                await msg.delete()
            except Exception:
                pass
    except Exception:
        pass


@bot.command(name="mirrorlog", aliases=["mlog"])
async def cmd_mirrorlog(ctx, count: int = 10):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    cid = ctx.channel.id
    entries = [x for x in _MIRROR_LOG if x["ch"] == cid][-count:]
    if not entries:
        await ctx.reply("Chưa có log.")
        return
    e = discord.Embed(title=f"📜 MIRROR LOG ({len(entries)})", color=ROYAL_GOLD)
    for i, x in enumerate(entries, 1):
        val = (x["content"][:80] or "*[ảnh/file]*")
        e.add_field(name=f"{i}. {x['author']}", value=f"{val}\n<t:{int(x['ts'])}:R>", inline=False)
    await ctx.send(embed=e)


@bot.command(name="mirrorclear")
async def cmd_mirrorclear(ctx):
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    _MIRROR_LOG.clear()
    await ctx.reply("🧹 Đã xóa log mirror.")


@bot.command(name="restore", aliases=["undo"])
async def cmd_restore(ctx, count: int = 1):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    cid = ctx.channel.id
    entries = [x for x in _MIRROR_LOG if x["ch"] == cid][-count:]
    if not entries:
        await ctx.reply("Không có gì.")
        return
    for x in entries:
        e = discord.Embed(color=0x36393F)
        e.set_author(name=x["author"], icon_url=x.get("avatar", ""))
        e.description = x["content"] or "*[không có text]*"
        if x["attachments"]:
            e.set_image(url=x["attachments"][0])
        e.set_footer(text=f"Restored · {datetime.fromtimestamp(x['ts']).strftime('%H:%M %d/%m')}")
        try:
            await ctx.send(embed=e)
        except Exception:
            continue
    await ctx.reply(f"✅ Khôi phục `{len(entries)}` tin")


@bot.command(name="restorewebhook", aliases=["rwh"])
async def cmd_restorewebhook(ctx, count: int = 5):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    cid = ctx.channel.id
    entries = [x for x in _MIRROR_LOG if x["ch"] == cid][-count:]
    if not entries:
        await ctx.reply("Không có gì.")
        return
    sent = 0
    for x in entries:
        try:
            await send_as_human(ctx.channel, x["content"] or "*[trống]*",
                                 name=x["author"], avatar=x.get("avatar", ""))
            sent += 1
            await asyncio.sleep(0.6)
        except Exception:
            continue
    await ctx.reply(f"✅ Gửi lại `{sent}/{len(entries)}`")


_afk_users = {}
_AFK_DELETE_MSG = True
_afk_lock = set()


@bot.command(name="afk")
async def cmd_afk(ctx, *, reason: str = "không lý do"):
    if not is_allowed(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    _afk_users.setdefault(ctx.guild.id, {})[ctx.author.id] = {
        "reason": reason[:200], "since": time.time()}
    await ctx.reply(f"💤 **{ctx.author.display_name}** AFK: *{reason[:200]}*")


@bot.command(name="unafk", aliases=["back"])
async def cmd_unafk(ctx):
    if not is_allowed(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    g = _afk_users.get(ctx.guild.id, {})
    if ctx.author.id in g:
        del g[ctx.author.id]
        await ctx.reply("👋 Trở lại rồi.")
    else:
        await ctx.reply("Mày có AFK đâu.")


@bot.command(name="afkstatus")
async def cmd_afkstatus(ctx):
    if not is_allowed(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    g = _afk_users.get(ctx.guild.id, {})
    if not g:
        await ctx.reply("Không ai AFK.")
        return
    e = discord.Embed(title="💤 DANH SÁCH AFK", color=ROYAL_GOLD)
    now = time.time()
    for uid, info in list(g.items())[:20]:
        try:
            u = await bot.fetch_user(int(uid))
            name = u.display_name
        except Exception:
            name = f"ID:{uid}"
        mins = int((now - info["since"]) / 60)
        e.add_field(name=name, value=f"`{mins}m` · {info['reason'][:80]}", inline=False)
    await ctx.send(embed=e)


@bot.command(name="afkdel")
async def cmd_afkdel(ctx, mode: str = None):
    global _AFK_DELETE_MSG
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if mode in ("on", "1", "bat"):
        _AFK_DELETE_MSG = True
        await ctx.reply("✅ AFK xóa tin gốc khi mention")
    elif mode in ("off", "0", "tat"):
        _AFK_DELETE_MSG = False
        await ctx.reply("❌ AFK chỉ reply")
    else:
        await ctx.reply(f"Hiện tại: {'ON' if _AFK_DELETE_MSG else 'OFF'}")


@bot.listen("on_message")
async def _afk_listener(msg):
    if msg.author.bot or not msg.guild:
        return
    g = _afk_users.get(msg.guild.id, {})
    if not g:
        return
    if msg.author.id in g and not msg.content.startswith(("!afk", "!unafk")):
        try:
            del g[msg.author.id]
            await msg.channel.send(f"👋 **{msg.author.display_name}** đã trở lại.",
                                    allowed_mentions=discord.AllowedMentions.none())
        except Exception:
            pass
    if not msg.content:
        return
    afk_hits = [(m, g[m.id]) for m in msg.mentions if m.id in g and m.id != msg.author.id]
    if not afk_hits:
        return
    cid = msg.channel.id
    if cid in _afk_lock:
        return
    _afk_lock.add(cid)
    try:
        me = msg.guild.me
        perms = msg.channel.permissions_for(me)
        for m, info in afk_hits:
            mins = int((time.time() - info["since"]) / 60)
            try:
                await msg.channel.send(
                    f"💤 **{m.display_name}** đang AFK ({mins}p): *{info['reason']}*",
                    allowed_mentions=discord.AllowedMentions.none())
            except Exception:
                pass
        if _AFK_DELETE_MSG and perms.manage_messages:
            try:
                content = msg.content
                author_name = msg.author.display_name
                author_avatar = msg.author.display_avatar.url
                for m, _ in afk_hits:
                    content = re.sub(rf"<@!?{m.id}>", f"@{m.display_name}", content)
                try:
                    await msg.delete()
                except Exception:
                    return
                if perms.manage_webhooks:
                    try:
                        await send_as_human(msg.channel, content[:2000] or "[trống]",
                                             name=author_name, avatar=author_avatar)
                        return
                    except Exception:
                        pass
                await msg.channel.send(f"**{author_name}**: {content[:1900] or '[trống]'}",
                                        allowed_mentions=discord.AllowedMentions.none())
            except Exception:
                pass
    finally:
        await asyncio.sleep(0.5)
        _afk_lock.discard(cid)


# ============================================================
# AUTO ROAST — LOOP
# ============================================================
async def auto_roast_loop(guild_id, channel_id, target_id, target_name,
                          interval, use_ai=False, gender="neutral"):
    mention = f"<@{target_id}>"
    job = _auto_job_get(guild_id, "roast")
    try:
        while True:
            if _auto_roast_targets.get(guild_id) != target_id:
                return
            try:
                channel = bot.get_channel(channel_id)
                if not channel:
                    return
                content = forge_roast(mention, tier=_AUTO_TIER,
                                       gender=gender, inject_zw=True)
                try:
                    if _is_human_on(channel.id):
                        ok = await send_as_human(channel, content)
                    else:
                        await channel.send(content)
                        ok = True
                    _stat_inc(guild_id, "roast", ok=bool(ok))
                    if job:
                        job.inc(ok=bool(ok))
                        await _auto_job_update(job)
                except (discord.errors.Forbidden, discord.errors.NotFound):
                    _stat_end(guild_id, "roast")
                    if job:
                        job.finish("cancelled")
                        await _auto_job_update(job, force=True)
                    return
                except discord.errors.HTTPException as e:
                    if e.status == 429:
                        ra = getattr(e, "retry_after", 2.0) or 2.0
                        await asyncio.sleep(min(ra, 5.0))
            except Exception as e:
                log.error("auto_roast: %s", e)
            await asyncio.sleep(interval * _R.uniform(0.75, 1.25))
    finally:
        _stat_end(guild_id, "roast")
        _auto_roast_targets.pop(guild_id, None)
        _roast_tasks.pop(guild_id, None)
        if job and job.status == "running":
            job.finish("done")
            try:
                await _auto_job_update(job, force=True)
            except Exception:
                pass


async def auto_fake_loop(guild_id, channel_id, target_id, interval, use_ai=False):
    fail_streak = 0
    job = _auto_job_get(guild_id, "fake")
    try:
        while True:
            if _fake_targets.get(guild_id) != (target_id, channel_id):
                return
            try:
                guild = bot.get_guild(guild_id)
                channel = bot.get_channel(channel_id)
                if not guild or not channel:
                    return
                target = guild.get_member(target_id)
                if not target:
                    try:
                        target = await guild.fetch_member(target_id)
                    except discord.NotFound:
                        return
                    except Exception:
                        await asyncio.sleep(interval)
                        continue
                burst_n = _R.randint(2, 3) if _R.random() < 0.35 else 1
                for b in range(burst_n):
                    if _fake_targets.get(guild_id) != (target_id, channel_id):
                        return
                    ok = await fake_send(channel, target, forge_fake())
                    _stat_inc(guild_id, "fake", ok=bool(ok))
                    if job:
                        job.inc(ok=bool(ok))
                    if not ok:
                        fail_streak += 1
                        if fail_streak >= 3:
                            return
                    else:
                        fail_streak = 0
                    if b < burst_n - 1:
                        await asyncio.sleep(_R.uniform(0.6, 1.3))
                if job:
                    await _auto_job_update(job)
            except Exception as e:
                log.error("auto_fake: %s", e)
            await asyncio.sleep(interval * _R.uniform(0.7, 1.3))
    finally:
        _stat_end(guild_id, "fake")
        _fake_targets.pop(guild_id, None)
        _fake_tasks.pop(guild_id, None)
        if job and job.status == "running":
            job.finish("done")
            try:
                await _auto_job_update(job, force=True)
            except Exception:
                pass


async def spamtin_loop(guild_id, channel_id, target_id, message, count, interval):
    fail = 0
    job = _auto_job_get(guild_id, "spamtin")
    try:
        guild = bot.get_guild(guild_id)
        channel = bot.get_channel(channel_id)
        if not guild or not channel:
            return
        target = guild.get_member(target_id)
        if not target:
            try:
                target = await guild.fetch_member(target_id)
            except Exception:
                return
        for i in range(count):
            if _spamtin_tasks.get(guild_id) != (target_id, channel_id, message):
                return
            content = message.replace("{i}", str(i + 1)).replace("{t}", target.display_name)
            if _R.random() < 0.5:
                content = f"{content} {_R.choice(_ZW)}"
            _ok = await fake_send(channel, target, content)
            _stat_inc(guild_id, "spamtin", ok=bool(_ok))
            if job:
                job.inc(ok=bool(_ok))
                await _auto_job_update(job)
            if not _ok:
                fail += 1
                if fail >= 5:
                    return
            else:
                fail = 0
            await asyncio.sleep(interval * _R.uniform(0.8, 1.2))
    except Exception as e:
        log.error("spamtin_loop: %s", e)
    finally:
        _stat_end(guild_id, "spamtin")
        _spamtin_tasks.pop(guild_id, None)
        if job and job.status == "running":
            job.finish("done")
            try:
                await _auto_job_update(job, force=True)
            except Exception:
                pass


async def spam_loop(guild_id, channel_id, target_id, count_per_burst, interval, use_ai=False):
    fail = 0
    job = _auto_job_get(guild_id, "spam")
    try:
        while True:
            if _spam_targets.get(guild_id) != (target_id, channel_id):
                return
            try:
                guild = bot.get_guild(guild_id)
                channel = bot.get_channel(channel_id)
                if not guild or not channel:
                    return
                target = guild.get_member(target_id)
                if not target:
                    try:
                        target = await guild.fetch_member(target_id)
                    except discord.NotFound:
                        return
                    except Exception:
                        await asyncio.sleep(interval)
                        continue
                for _ in range(count_per_burst):
                    if _spam_targets.get(guild_id) != (target_id, channel_id):
                        return
                    ok = await fake_send(channel, target, forge_fake())
                    _stat_inc(guild_id, "spam", ok=bool(ok))
                    if job:
                        job.inc(ok=bool(ok))
                    if ok:
                        fail = 0
                    else:
                        fail += 1
                        if fail >= 5:
                            return
                    await asyncio.sleep(_R.uniform(0.5, 1.2))
                if job:
                    await _auto_job_update(job)
            except Exception as e:
                log.error("spam_loop: %s", e)
            await asyncio.sleep(interval * _R.uniform(0.85, 1.15))
    finally:
        _stat_end(guild_id, "spam")
        _spam_targets.pop(guild_id, None)
        _fake_tasks.pop(f"spam_{guild_id}", None)
        if job and job.status == "running":
            job.finish("done")
            try:
                await _auto_job_update(job, force=True)
            except Exception:
                pass


# ============================================================
# COMMANDS — AutoJob + Embed live
# ============================================================
@bot.command(name="autochui", aliases=["autoroast", "chuilien"])
async def cmd_autochui(ctx, member: discord.Member = None, interval: str = None, use_ai: str = ""):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.guild or not member:
        await ctx.reply("Dùng: `!autochui @user [giây]`")
        return
    if member.id in (bot.user.id, ctx.author.id):
        await ctx.reply("Tự chửi à?")
        return

    interval = _parse_interval(interval, 1.2, 0.8, 60.0)
    existing = _roast_tasks.get(ctx.guild.id)
    if existing and not existing.done():
        existing.cancel()
        await asyncio.sleep(0.2)

    gender = detect_gender(member)
    _stat_init(ctx.guild.id, "roast",
               target=member.id,
               target_name=member.display_name,
               channel_id=ctx.channel.id,
               gender=gender)
    _auto_roast_targets[ctx.guild.id] = member.id

    job = AutoJob("roast", ctx.guild.id, ctx.channel.id,
                  member.id, member.display_name, interval,
                  gender=gender)
    _auto_job_set(job)

    e = _auto_job_embed(job)
    msg = await ctx.send(embed=e)
    job.message_id = msg.id

    _roast_tasks[ctx.guild.id] = asyncio.create_task(
        auto_roast_loop(ctx.guild.id, ctx.channel.id, member.id,
                        member.display_name, interval, False, gender))

    asyncio.create_task(_auto_job_refresh_loop(job))


@bot.command(name="stopchui", aliases=["stoproast"])
async def cmd_stopchui(ctx):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    task = _roast_tasks.pop(ctx.guild.id, None)
    _auto_roast_targets.pop(ctx.guild.id, None)
    _stat_end(ctx.guild.id, "roast")
    job = _auto_job_get(ctx.guild.id, "roast")
    if job:
        job.finish("cancelled")
        await _auto_job_update(job, force=True)
        _auto_job_del(ctx.guild.id, "roast")
    if task and not task.done():
        task.cancel()
        await ctx.send(
            "⚔️ **TRẪM ĐÃ THU ĐAO**\n"
            "-# Máu đã ngừng đổ. Thằng lol kia còn sống, nhưng nhục đéo gì nữa.")
    else:
        await ctx.reply("⚔️ Không có gì chạy. Đao còn trong vỏ.")


@bot.command(name="roast", aliases=["chui", "insult", "si"])
async def cmd_roast(ctx, member: discord.Member = None, tier: str = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not member:
        await ctx.reply("Dùng: `!chui @user [nhe|vua|nang|huydiet|mega]`")
        return
    if member.id in (bot.user.id, ctx.author.id):
        await ctx.reply("Tự chửi à?")
        return
    mention = f"<@{member.id}>"
    g = detect_gender(member)
    async with ctx.typing():
        if tier == "mega":
            txt = forge_roast_mega(mention, gender=g)
        else:
            txt = forge_roast(mention, tier=tier, gender=g)
        if _is_human_on(ctx.channel.id):
            await send_as_human(ctx.channel, txt)
        else:
            await ctx.send(txt)


@bot.command(name="combo", aliases=["chuicombo", "roastcombo"])
async def cmd_combo(ctx, member: discord.Member = None, lines: int = 6):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not member:
        await ctx.reply("Dùng: `!combo @user [số_câu 4-12]`")
        return
    if member.id in (bot.user.id, ctx.author.id):
        await ctx.reply("Tự chửi à?")
        return
    mention = f"<@{member.id}>"
    g = detect_gender(member)
    async with ctx.typing():
        txt = forge_roast_combo(mention, gender=g, lines=lines)
        if _is_human_on(ctx.channel.id):
            await send_as_human(ctx.channel, txt)
        else:
            await ctx.send(txt)


@bot.command(name="megachui", aliases=["megaroast"])
async def cmd_megachui(ctx, member: discord.Member = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not member or member.id in (bot.user.id, ctx.author.id):
        return
    mention = f"<@{member.id}>"
    g = detect_gender(member)
    async with ctx.typing():
        for _ in range(3):
            txt = forge_roast_mega(mention, gender=g)
            if _is_human_on(ctx.channel.id):
                await send_as_human(ctx.channel, txt)
            else:
                await ctx.send(txt)
            await asyncio.sleep(1.2)


@bot.command(name="roastall", aliases=["chuihet"])
async def cmd_roastall(ctx):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    members = [m for m in ctx.guild.members if not m.bot and m.id not in (ctx.author.id, bot.user.id)]
    if not members:
        await ctx.reply("⚔️ Thành này vắng hoe.")
        return
    _R.shuffle(members)
    await ctx.send(f"⚔️ **BỐ KHAI ĐAO** — {min(5, len(members))} phàm phu:")
    for m in members[:5]:
        try:
            g = detect_gender(m)
            txt = forge_roast(f"<@{m.id}>", tier="huydiet", gender=g)
            if _is_human_on(ctx.channel.id):
                await send_as_human(ctx.channel, txt)
            else:
                await ctx.send(txt)
        except Exception:
            pass
        await asyncio.sleep(1.2)


@bot.command(name="setgender", aliases=["gender"])
async def cmd_setgender(ctx, member: discord.Member = None, g: str = None):
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not member or not g:
        await ctx.reply("Dùng: `!setgender @user <nam|nu|neutral>`")
        return
    g = g.lower()
    if g not in ("nam", "nu", "neutral"):
        await ctx.reply("Chọn nam, nu hoặc neutral.")
        return
    set_gender_db(member.id, g)
    await ctx.reply(f"✅ `{member.display_name}` = `{g}`")


@bot.command(name="checkgender")
async def cmd_checkgender(ctx, member: discord.Member = None):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    m = member or ctx.author
    await ctx.reply(f"`{m.display_name}` → `{detect_gender(m)}`")


@bot.command(name="roastdb", aliases=["roaststats"])
async def cmd_roastdb(ctx):
    if not is_allowed(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    e = discord.Embed(title="📊  ROAST DB v7.2", color=ROYAL_GOLD)
    e.add_field(name="Body", value=str(len(_BODY_LINES)), inline=True)
    e.add_field(name="Openers", value=str(len(_OPENERS_BASE)), inline=True)
    e.add_field(name="Closers", value=str(len(_CLOSERS_BASE)), inline=True)
    e.add_field(name="Gender", value=str(sum(len(v) for v in _ATTACK_GENDER.values())), inline=True)
    e.add_field(name="Used", value=f"`{len(_used_lines)}`", inline=True)
    e.add_field(name="Fake", value=str(len(_FAKE_1P_TEMPLATES)), inline=True)
    total = (len(_BODY_LINES) + sum(len(v) for v in _ATTACK_GENDER.values()) +
             len(_OPENERS_BASE) + len(_CLOSERS_BASE))
    e.add_field(name="Tổng", value=f"`{total}` câu", inline=False)
    e.add_field(name="Auto mode", value="`1 câu / lần`", inline=False)
    await ctx.send(embed=e)


@bot.command(name="resetroast")
async def cmd_resetroast(ctx):
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    _used_lines.clear()
    _used_openers.clear()
    _used_closers.clear()
    await ctx.reply("✅ Đã reset pool.")


@bot.command(name="maxpower")
async def cmd_maxpower(ctx):
    global _AUTO_ZW_INJECT
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    _AUTO_ZW_INJECT = 0.7
    await ctx.send("🔥 **MAX POWER** — 1 câu / lần, savage tối đa")


@bot.command(name="autoconfig")
async def cmd_autoconfig(ctx, key: str = None, value: str = None):
    global _AUTO_ZW_INJECT
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not key:
        e = discord.Embed(title="⚙️  AUTO CONFIG (v7.2)", color=ROYAL_GOLD)
        e.add_field(name="Mode", value="`1 câu / lần`", inline=True)
        e.add_field(name="Tier", value=f"`{_AUTO_TIER}`", inline=True)
        e.add_field(name="ZW", value=f"`{int(_AUTO_ZW_INJECT*100)}%`", inline=True)
        await ctx.send(embed=e)
        return
    key = key.lower()
    try:
        if key == "zw":
            v = float(str(value).replace(",", ".").rstrip("%"))
            v = max(0.0, min(1.0, v / 100 if v > 1 else v))
            _AUTO_ZW_INJECT = v
            await ctx.reply(f"✅ `zw` = `{int(v*100)}%`")
        else:
            await ctx.reply("key: zw (0-100)")
    except Exception:
        await ctx.reply("Số sai.")


@bot.command(name="fake", aliases=["gia"])
async def cmd_fake(ctx, *, args: str = None):
    global HUMAN_NAME
    if not args:
        await ctx.reply(
            "**FAKE / WEBHOOK**\n"
            "`!fake @user [text]` — fake tin\n"
            "`!fake on` — bật webhook\n"
            "`!fake off` — tắt webhook\n"
            "`!fake status` — xem pool\n"
            "`!fake rebuild` — tạo lại pool\n"
            "`!fake name <tên|@user>` — đổi tên human")
        return

    args = args.strip()
    if not args:
        await ctx.reply("Thiếu tham số.")
        return

    first = args.split(None, 1)[0].lower() if args else ""
    rest = args[len(first):].strip() if first else ""

    if first in ("on", "bat", "bật", "1"):
        if not is_admin(ctx.author) or not ctx.guild:
            await ctx.reply(pick_perm_insult())
            return
        _HUMAN_ENABLED[ctx.channel.id] = True
        await ctx.reply("🎭 Webhook **BẬT** — bot sẽ giả làm user.")
        return

    if first in ("off", "tat", "tắt", "0"):
        if not is_admin(ctx.author) or not ctx.guild:
            await ctx.reply(pick_perm_insult())
            return
        _HUMAN_ENABLED[ctx.channel.id] = False
        await ctx.reply("🤖 Webhook **TẮT** — bot sẽ trả lời bình thường.")
        return

    if first in ("status", "st", "info"):
        if not is_allowed(ctx.author) or not ctx.guild:
            await ctx.reply(pick_perm_insult())
            return
        cid = ctx.channel.id
        try:
            await _pool_get(ctx.channel)
        except Exception:
            pass
        pool = _wh_pool.get(cid, [])
        alive = [e for e in pool if e["fails"] < 5]
        me = ctx.guild.me
        perms = ctx.channel.permissions_for(me)
        e = discord.Embed(title="🎭 FAKE / HUMAN", color=ROYAL_GOLD)
        e.add_field(name="Trạng thái",
                    value="🎭 BẬT (webhook)" if _is_human_on(cid) else "🤖 TẮT (bot)",
                    inline=True)
        e.add_field(name="Tên Human", value=f"`{HUMAN_NAME}`", inline=True)
        e.add_field(name="Pool", value=f"`{len(alive)}/{_POOL_SIZE}`", inline=True)
        e.add_field(name="Quyền Webhook",
                    value="✅ OK" if perms.manage_webhooks else "❌ THIẾU",
                    inline=False)
        await ctx.send(embed=e)
        return

    if first in ("rebuild", "rb", "reset"):
        if not is_admin(ctx.author) or not ctx.guild:
            await ctx.reply(pick_perm_insult())
            return
        me = ctx.guild.me
        if not ctx.channel.permissions_for(me).manage_webhooks:
            await ctx.reply("❌ Thiếu quyền Manage Webhooks.")
            return
        old = _wh_pool.pop(ctx.channel.id, [])
        cnt = 0
        for e in old:
            try:
                await e["wh"].delete()
                cnt += 1
            except Exception:
                pass
        pool = await _pool_get(ctx.channel)
        await ctx.send(f"🔁 Xoá `{cnt}` · Tạo `{len(pool)}`")
        return

    if first in ("name", "ten", "tên"):
        if not is_owner(ctx.author):
            await ctx.reply(pick_perm_insult())
            return
        if not rest:
            await ctx.reply(f"Tên hiện tại: `{HUMAN_NAME}`")
            return
        m2 = re.match(r"^<@!?(\d+)>$", rest)
        if m2:
            try:
                uid = int(m2.group(1))
                u = ctx.guild.get_member(uid) if ctx.guild else None
                if not u:
                    u = await bot.fetch_user(uid)
                rest = u.display_name or u.name
            except Exception:
                await ctx.reply("Không tìm được user.")
                return
        HUMAN_NAME = rest[:80]
        if ctx.guild:
            old = _wh_pool.pop(ctx.channel.id, [])
            for e in old:
                try:
                    await e["wh"].delete()
                except Exception:
                    pass
            try:
                await _pool_get(ctx.channel)
            except Exception:
                pass
        await ctx.reply(f"✅ Tên → `{HUMAN_NAME}`")
        return

    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.guild:
        await ctx.reply("Chỉ dùng trong server.")
        return

    m = re.match(r"^<@!?(\d+)>\s*(.*)$", args, re.DOTALL)
    if not m:
        await ctx.reply(
            "❌ Cú pháp sai.\n"
            "`!fake @user [text]` — fake tin\n"
            "`!fake on|off|status|rebuild|name` — quản lý")
        return

    uid = int(m.group(1))
    text = (m.group(2) or "").strip() or None

    member = ctx.guild.get_member(uid)
    if not member:
        try:
            member = await ctx.guild.fetch_member(uid)
        except Exception:
            await ctx.reply("Không tìm thấy user.")
            return

    if member.id == bot.user.id:
        return

    content = text if text else forge_fake()
    if await fake_send(ctx.channel, member, content):
        try:
            await ctx.message.delete()
        except Exception:
            pass
    else:
        await ctx.reply("💀 Thất bại.")


@bot.command(name="fakecombo", aliases=["giacombo"])
async def cmd_fakecombo(ctx, member: discord.Member = None):
    if not is_admin(ctx.author) or not ctx.guild or not member:
        await ctx.reply(pick_perm_insult())
        return
    if member.id == bot.user.id:
        return
    for ln in _R.choice(_FAKE_1P_COMBO):
        if not await fake_send(ctx.channel, member, ln):
            break
        await asyncio.sleep(_R.uniform(0.8, 1.5))


@bot.command(name="autofake", aliases=["autogia"])
async def cmd_autofake(ctx, member: discord.Member = None, interval: str = None, use_ai: str = ""):
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.guild or not member or member.id == bot.user.id:
        return
    interval = _parse_interval(interval, 2.0, 1.2, 60.0)
    me = ctx.guild.me
    if not ctx.channel.permissions_for(me).manage_webhooks:
        await ctx.reply("Thiếu quyền Manage Webhooks.")
        return
    existing = _fake_tasks.get(ctx.guild.id)
    if existing and not existing.done():
        existing.cancel()
        await asyncio.sleep(0.2)
    _stat_init(ctx.guild.id, "fake",
               target=member.id,
               target_name=member.display_name,
               channel_id=ctx.channel.id)
    _fake_targets[ctx.guild.id] = (member.id, ctx.channel.id)

    job = AutoJob("fake", ctx.guild.id, ctx.channel.id,
                  member.id, member.display_name, interval)
    _auto_job_set(job)

    e = _auto_job_embed(job)
    msg = await ctx.send(embed=e)
    job.message_id = msg.id

    _fake_tasks[ctx.guild.id] = asyncio.create_task(
        auto_fake_loop(ctx.guild.id, ctx.channel.id, member.id, interval, False))

    asyncio.create_task(_auto_job_refresh_loop(job))


@bot.command(name="stopfake")
async def cmd_stopfake(ctx):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    task = _fake_tasks.pop(ctx.guild.id, None)
    _fake_targets.pop(ctx.guild.id, None)
    _stat_end(ctx.guild.id, "fake")
    job = _auto_job_get(ctx.guild.id, "fake")
    if job:
        job.finish("cancelled")
        await _auto_job_update(job, force=True)
        _auto_job_del(ctx.guild.id, "fake")
    if task and not task.done():
        task.cancel()
        await ctx.send(
            "🎭 **TRẪM ĐÃ THÁO MẶT NẠ**\n"
            "-# Màn kịch kết thúc. Thằng lol kia quay về làm chính nó, đéo ai buồn giả nữa.")
    else:
        await ctx.reply("🎭 Đéo có màn kịch nào đang diễn.")


@bot.command(name="spamtin", aliases=["spammsg"])
async def cmd_spamtin(ctx, member: discord.Member = None, count: str = None,
                     interval: str = None, *, message: str = None):
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.guild or not member or not message or member.id == bot.user.id:
        return
    try:
        c = max(1, min(200, int(count) if count else 20))
    except Exception:
        c = 20
    iv = _parse_interval(interval, 1.5, 0.5, 60.0)
    me = ctx.guild.me
    if not ctx.channel.permissions_for(me).manage_webhooks:
        await ctx.reply("Thiếu quyền Manage Webhooks.")
        return
    _stat_init(ctx.guild.id, "spamtin",
               target=member.id,
               target_name=member.display_name,
               channel_id=ctx.channel.id,
               total=c)
    _spamtin_tasks[ctx.guild.id] = (member.id, ctx.channel.id, message)

    job = AutoJob("spamtin", ctx.guild.id, ctx.channel.id,
                  member.id, member.display_name, iv,
                  total=c, message=message[:50])
    _auto_job_set(job)

    e = _auto_job_embed(job)
    msg = await ctx.send(embed=e)
    job.message_id = msg.id

    asyncio.create_task(spamtin_loop(ctx.guild.id, ctx.channel.id, member.id, message, c, iv))

    asyncio.create_task(_auto_job_refresh_loop(job))


@bot.command(name="stopspamtin")
async def cmd_stopspamtin(ctx):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    _stat_end(ctx.guild.id, "spamtin")
    job = _auto_job_get(ctx.guild.id, "spamtin")
    if job:
        job.finish("cancelled")
        await _auto_job_update(job, force=True)
        _auto_job_del(ctx.guild.id, "spamtin")
    if _spamtin_tasks.pop(ctx.guild.id, None):
        await ctx.send(
            "📮 **TRẪM ĐÃ NGỪNG RÓT CHỮ**\n"
            "-# Từng con chữ như dao phủ đã ngừng rơi. Thằng lol kia thở được rồi.")
    else:
        await ctx.reply("📮 Đéo có cơn bão chữ nào đang thổi.")


@bot.command(name="spam", aliases=["spamfake"])
async def cmd_spam(ctx, member: discord.Member = None, count: str = None,
                  interval: str = None, use_ai: str = ""):
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.guild or not member or member.id == bot.user.id:
        return
    try:
        cpb = max(1, min(20, int(count))) if count else 5
    except Exception:
        cpb = 5
    iv = _parse_interval(interval, 15.0, 5.0, 300.0)
    me = ctx.guild.me
    if not ctx.channel.permissions_for(me).manage_webhooks:
        await ctx.reply("Thiếu quyền Manage Webhooks.")
        return
    old = _fake_tasks.get(f"spam_{ctx.guild.id}")
    if old and not old.done():
        old.cancel()
        await asyncio.sleep(0.2)
    _stat_init(ctx.guild.id, "spam",
               target=member.id,
               target_name=member.display_name,
               channel_id=ctx.channel.id,
               burst=cpb)
    _spam_targets[ctx.guild.id] = (member.id, ctx.channel.id)

    job = AutoJob("spam", ctx.guild.id, ctx.channel.id,
                  member.id, member.display_name, iv,
                  burst=cpb)
    _auto_job_set(job)

    e = _auto_job_embed(job)
    msg = await ctx.send(embed=e)
    job.message_id = msg.id

    _fake_tasks[f"spam_{ctx.guild.id}"] = asyncio.create_task(
        spam_loop(ctx.guild.id, ctx.channel.id, member.id, cpb, iv, False))

    asyncio.create_task(_auto_job_refresh_loop(job))


@bot.command(name="stopspam")
async def cmd_stopspam(ctx):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    task = _fake_tasks.pop(f"spam_{ctx.guild.id}", None)
    _spam_targets.pop(ctx.guild.id, None)
    _stat_end(ctx.guild.id, "spam")
    job = _auto_job_get(ctx.guild.id, "spam")
    if job:
        job.finish("cancelled")
        await _auto_job_update(job, force=True)
        _auto_job_del(ctx.guild.id, "spam")
    if task and not task.done():
        task.cancel()
        await ctx.send(
            "💥 **TRẪM ĐÃ NGỪNG NÉM BOM**\n"
            "-# Mặt thằng lol kia còn nguyên, tiếc thật.")
    else:
        await ctx.reply("💥 Đéo có quả bom nào đang nổ.")


@bot.command(name="burst", aliases=["no"])
async def cmd_burst(ctx, member: discord.Member = None, count: int = 10):
    if not is_admin(ctx.author):
        await ctx.reply(pick_perm_insult())
        return
    if not ctx.guild or not member or member.id == bot.user.id:
        return
    count = max(1, min(50, count))
    if not ctx.channel.permissions_for(ctx.guild.me).manage_webhooks:
        await ctx.reply("Thiếu quyền Manage Webhooks.")
        return
    status = await ctx.send(f"💥 Nổ `{count}` tin...")
    ok = 0
    for _ in range(count):
        if await fake_send(ctx.channel, member, forge_fake()):
            ok += 1
        await asyncio.sleep(_R.uniform(0.5, 1.3))
    try:
        await status.edit(content=f"💥 `{ok}/{count}`")
    except Exception:
        pass


@bot.command(name="stats", aliases=["tk", "thongke", "kpi"])
async def cmd_stats(ctx, member: discord.Member = None):
    if not is_allowed(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    gid = ctx.guild.id
    data = _stat_get(gid)
    if not data:
        await ctx.reply("📊 Trẫm chưa mở chiến dịch nào.")
        return
    now = time.time()
    e = discord.Embed(
        title="📊  BẢNG VÀNG CHIẾN TÍCH  📊",
        color=ROYAL_GOLD,
        timestamp=discord.utils.utcnow())
    e.description = "Mọi hành động của trẫm đều khắc vào sử sách:"
    kind_label = {
        "roast": "⚔️ Auto Chửi",
        "fake": "🎭 Auto Fake",
        "spam": "💥 Spam Burst",
        "spamtin": "📮 Spam Tin",
    }
    total_sent = 0
    total_failed = 0
    for kind, s in data.items():
        label = kind_label.get(kind, kind)
        running = s.get("ended") is None
        status = "🔥 ĐANG CHẠY" if running else "✅ ĐÃ DỪNG"
        dur = int((s.get("ended") or now) - s.get("started", now))
        target_name = s.get("target_name", "?")
        target_id = s.get("target")
        target_txt = f"<@{target_id}>" if target_id else "`?`"
        sent = s.get("sent", 0)
        failed = s.get("failed", 0)
        total_sent += sent
        total_failed += failed
        rate = 0.0
        if dur > 0:
            rate = round(sent / dur * 60, 1)
        last_gap = ""
        if s.get("last_sent"):
            gap = int(now - s["last_sent"])
            last_gap = f"\n🕐 Tin cuối: `{gap}s` trước"
        val = (
            f"🎯 Mục tiêu: {target_txt} (`{target_name[:30]}`)\n"
            f"📤 Đã bắn: **`{sent}`** tin · ❌ Fail: `{failed}`\n"
            f"⏱️ Chạy: `{dur}s` · Tốc độ: `{rate}/phút`\n"
            f"Trạng thái: **{status}**{last_gap}"
        )
        e.add_field(name=label, value=val, inline=False)
    e.add_field(
        name="🏆 TỔNG KẾT",
        value=f"📤 Tổng tin đã bắn: **`{total_sent}`**\n"
              f"❌ Tổng fail: `{total_failed}`",
        inline=False)
    e.set_footer(text="⚔️ Gõ !stats để cập nhật · !stopall để dừng hết")
    await ctx.send(embed=e)


@bot.command(name="statsreset", aliases=["tkreset", "xoatk"])
async def cmd_statsreset(ctx):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    with _stats_lock:
        _op_stats.pop(ctx.guild.id, None)
    await ctx.reply("🧹 Đã xoá bảng vàng chiến tích.")


@bot.command(name="stopall", aliases=["stophet"])
async def cmd_stopall(ctx):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    gid = ctx.guild.id
    stopped = []
    t = _roast_tasks.pop(gid, None)
    if t and not t.done():
        t.cancel()
        stopped.append("chửi")
    _auto_roast_targets.pop(gid, None)
    _stat_end(gid, "roast")
    t = _fake_tasks.pop(gid, None)
    if t and not t.done():
        t.cancel()
        stopped.append("fake")
    _fake_targets.pop(gid, None)
    _stat_end(gid, "fake")
    t = _fake_tasks.pop(f"spam_{gid}", None)
    if t and not t.done():
        t.cancel()
        stopped.append("spam")
    _spam_targets.pop(gid, None)
    _stat_end(gid, "spam")
    if _spamtin_tasks.pop(gid, None):
        stopped.append("spamtin")
    _stat_end(gid, "spamtin")

    for kind in ("roast", "fake", "spam", "spamtin"):
        job = _auto_job_get(gid, kind)
        if job:
            job.finish("cancelled")
            try:
                await _auto_job_update(job, force=True)
            except Exception:
                pass
            _auto_job_del(gid, kind)

    if stopped:
        await ctx.send(
            f"⚔️ **TRẪM ĐÃ THU TOÀN BỘ BINH**\n"
            f"-# Tắt: `{', '.join(stopped)}` · Tha mạng cho cả server hôm nay.")
    else:
        await ctx.reply("⚔️ Đéo có gì chạy. Đao kiếm còn nguyên trong vỏ.")


@bot.command(name="whstatus")
async def cmd_whstatus(ctx):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    pool = _wh_pool.get(ctx.channel.id, [])
    alive = [e for e in pool if e["fails"] < 5]
    await ctx.send(f"📦 Pool: `{len(alive)}/{_POOL_SIZE}`")


@bot.command(name="whdebug")
async def cmd_whdebug(ctx):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    ch = ctx.channel
    me = ctx.guild.me
    perms = ch.permissions_for(me)
    e = discord.Embed(title="🔍 WEBHOOK DEBUG", color=ROYAL_GOLD)
    e.add_field(name="Quyền Manage Webhooks",
                value="✅ CÓ" if perms.manage_webhooks else "❌ THIẾU", inline=False)
    try:
        whs = await ch.webhooks()
        bot_whs = [w for w in whs if w.user and w.user.id == bot.user.id]
        e.add_field(name="Webhook của bot", value=f"`{len(bot_whs)}`", inline=False)
    except Exception as ex:
        e.add_field(name="Webhook list", value=f"❌ `{str(ex)[:100]}`", inline=False)
    pool = _wh_pool.get(ch.id, [])
    alive = [x for x in pool if x["fails"] < 5]
    e.add_field(name="Pool", value=f"`{len(alive)}/{_POOL_SIZE}`", inline=False)
    e.add_field(name="Human mode", value="BẬT" if _is_human_on(ch.id) else "TẮT", inline=False)
    await ctx.send(embed=e)


@bot.command(name="whrebuild")
async def cmd_whrebuild(ctx):
    if not is_admin(ctx.author) or not ctx.guild:
        await ctx.reply(pick_perm_insult())
        return
    old = _wh_pool.pop(ctx.channel.id, [])
    count = 0
    for entry in old:
        try:
            await entry["wh"].delete()
            count += 1
        except Exception:
            pass
    pool = await _pool_get(ctx.channel)
    await ctx.send(f"🔁 Xoá `{count}` · Tạo `{len(pool)}`")


@tasks.loop(minutes=30)
async def pool_cleanup_task():
    for cid, pool in list(_wh_pool.items()):
        _wh_pool[cid] = [e for e in pool if e["fails"] < 5]
        for entry in [e for e in pool if e["fails"] >= 5]:
            try:
                await entry["wh"].delete()
            except Exception:
                pass


@tasks.loop(hours=6)
async def stats_cleanup_task():
    """✅ FIX v7.2: Dọn stats cũ hơn 24h."""
    try:
        _stat_cleanup()
    except Exception:
        pass


def audit(uid, action, detail=""):
    try:
        db_run("INSERT INTO audit(user_id, action, detail, ts) VALUES(?,?,?,?)",
               (int(uid), action[:80], str(detail)[:500], time.time()))
    except Exception:
        pass


log.info("RUN BOT GAY — CORE v7.2 OK (BÁ VƯƠNG AUTO JOB TRACKING + STATS CLEANUP)")