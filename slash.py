# slash.py — FULL v71.2
# SPAM MỌI NƠI: DM · Group DM · Guild bất kỳ (chỉ cần Send Messages)
# Auto-tag user · Chữ bự (heading 1) · Tag được everyone/here
# Retry 429 vô hạn — KHÔNG ngắt sau 5 câu
# PANEL EPHEMERAL — chỉ mình bạn thấy, spam vẫn public.

import functools, inspect, io, random, asyncio, re, time, aiohttp, discord
from discord import app_commands
import sys

# ============================================================
# LẤY CONTEXT TỪ MAIN
# ============================================================
_shared_ctx = sys.modules.get('__main__')
if _shared_ctx and hasattr(_shared_ctx, '__dict__'):
    _shared_ctx = _shared_ctx.__dict__.get('shared', {})
else:
    _shared_ctx = {}

bot = _shared_ctx.get('bot')
is_admin = _shared_ctx.get('is_admin', lambda u: False)
is_allowed = _shared_ctx.get('is_allowed', lambda u: False)
log = _shared_ctx.get('log')

if bot is None:
    raise RuntimeError("slash.py: bot chưa init — check main.py load order")


# ============================================================
# STATE
# ============================================================
_ACTIVE_RAIDS = {}


# ============================================================
# POOL MẶC ĐỊNH
# ============================================================
_DEFAULT_LINES_RAW = """cút mẹ mày về nhà đi
cái loại mày ra đời người ta khinh như rác rưởi mà về mạng vẫn gáy hăng nhỉ
bố mẹ mày oằn lưng gánh cái cục nợ này chắc còng cả sống lưng rồi đấy
bớt cái mõm lại đi con giời, nghe mày sủa mà tao thấy tội nghiệp cho cái não mày
nhắm đú lại ai không mà cứ nhảy vào họng người ta ngồi thế hả thằng ranh
mặt thì đần, nết thì hãm, đéo hiểu sao vẫn tự tin vác cái mặt ra đây gáy được
nhìn lại bản thân xem có cái tích sự gì cho đời chưa mà mở mồm ra dạy đời người khác
nói thật chứ loại mày cho đống phân còn thấy lãng phí tài nguyên đất nước
con người hơn con vật ở cái não, còn mày thì đéo thấy cái nếp nhăn nào luôn
ra đường thì câm như hến, lên mạng thì cào phím như đúng rồi, đúng loại hèn
cái dòng họ nhà mày chắc cũng bất lực vì đẻ ra được cái thứ ăn hại như mày
gáy to lên em ơi, gáy cho thiên hạ người ta biết mày thiếu học cỡ nào
mở mồm ra câu nào là thấy mùi thất học bốc lên nồng nặc câu đấy
sống chật đất tốn oxy, làm cái gì cũng hỏng mà đòi lên mặt với ai
tao nói thật mày nên soi gương tự tát vào mặt vài cái cho nó tỉnh ngộ ra đi
tuổi thì ranh, kinh nghiệm thì đéo có, chỉ giỏi cái nết trơ trẽn vô liêm sỉ
loại mày có cho làm cảnh người ta cũng chê vì nhìn nó hãm tài quá
đụng đâu hỏng đó, báo nhà báo cửa xong lên mạng làm như mình ngon lắm
cút về bú sữa mẹ tiếp đi em ơi, xã hội này đéo có chỗ cho loại óc bã đậu đâu
nói câu nào người ta khinh câu đấy mà vẫn nhơn nhơn cái mặt ra được, bái phục
cái loại ăn cháo đá bát, sống không có tí đạo đức nào thì biến mẹ mày đi
nhắm nói chuyện đàng hoàng đéo được thì ngậm cái mõm lại cho nước nó trong
người ta tát cho vào mặt thì lại bảo tại số, trong khi cái nết hãm đéo chịu được
mày nghĩ mày là ai vậy? một cục nợ vô dụng thích gây sự chú ý à
ảo tưởng ít thôi em, ra đời tao e là mày đéo sống nổi qua 5 phút đâu
cái loại tiểu nhân đớn hèn, chỉ giỏi núp sau màn hình rủa thầm người khác
nhục nhã vừa thôi, để phần cho người khác người ta còn sống với chứ
địt cái lol nhà m
m là thk thất hc óc chim
cặc bé cx lên tiếng à
lồn mấy tháng chưa rửa r e ở xa thế mà còn nghe khắm chán
dòng họ nhà m t địt quài chán vl
óc thế não này thua cả con ruồi đầy cứt
tuổi tuất à sao phải thở bằng mồm thúi của m nhỉ
não iq chx đc 20 sủa ẳng ăng đây chi vậy
đcm m thì bt cái dell gì thk ngu
chả hiểu gì tưởng mình bt hết ảo vl
ảo tưởng bản thân có gì vậy?
nchuyen nghe nhục vãi đái
mẹ thk óc mở mồm ra câu nào cx bt mình ngu
gia đình m ko nên đẻ ra m
m là con tinh trùng tệ bạc nhất mà con mẹ m thụ ra đc
oai cái dell gì vậy lmao
kid sủa đây làm gì vậy e
óc chim sủa gì vậy
ba mẹ e chx dạy e baoh về cuộc sống con ng à
sống mà thua cả con chó phản bội chủ nữa
var cl gì, bản thân e chs sao lại đc
ba mẹ m chưa 44 là ngon r lên đây sủa cc
đcm địt con mẹ m
chó mất dạy
thk ngu óc cặc
lồn mẹ m
mã nhà m tao chx đi thăm mà m còn lên sủa
óc chó nói thế cx chả hiểu
thk chó óc chim
cay đi e ơi
cay thì làm đc dell gì a nè
khóc to vào
nói với cha mẹ con thua r
L kid gáy dell gì
tuổi trẻ ở nhà là tốt
học ngu lên đây sủa bậy?
nhìn m có nét đẹp nào ko?
ảo tưởng bản thân?
m nghĩ m đẹp?
mẹ nghe tệ hại vl
nghĩ ra t nói chuyện với m t cx bị bẩn ra
cay đi e
địt tổ sư m
chó kid ngu vl lmao
sủa nx đi to vào
44 đi e ơi
sốg kiểu như e tốn
next cụ m đi
óc cặc lên sủa bậy ẳng hay vào
nhìn m tệ hại vl"""

_DEFAULT_LINES = [l.strip() for l in _DEFAULT_LINES_RAW.strip().split("\n") if l.strip()]


# ============================================================
# PERM
# ============================================================
_NO_PERM_MSG = "cút con đỉ mẹ m đi thk ngu, tuổi lồn chạm vào lệnh của bố mày"


async def _check_perm(interaction: discord.Interaction):
    try:
        if is_admin(interaction.user) or is_allowed(interaction.user):
            return True
        try:
            await interaction.response.send_message(_NO_PERM_MSG, ephemeral=True)
        except Exception:
            pass
        return False
    except Exception:
        return True


# ============================================================
# STATE HELPERS
# ============================================================
def _ensure_state(channel_id, target_id=None, target_mention=None):
    """Trả về state cho channel; tạo mới nếu chưa có (không reset config cũ)."""
    st = _ACTIVE_RAIDS.get(channel_id)
    if st is None:
        st = {
            "target_id": target_id,
            "target_mention": target_mention or "<@0>",
            "lines": list(_DEFAULT_LINES),
            "link": None,
            "gif": None,
            "delay": 1.2,
            "interaction": None,
            "task": None,
        }
        _ACTIVE_RAIDS[channel_id] = st
    else:
        if target_id is not None:
            st["target_id"] = target_id
        if target_mention is not None:
            st["target_mention"] = target_mention
    return st


# ============================================================
# BUILD CONTENT
# ============================================================
def _build_content(raw: str, target_mention: str, link: str = "", gif: str = "") -> str:
    raw = (raw or "").strip()

    has_mention = (
        "<@" in raw
        or "@everyone" in raw.lower()
        or "@here" in raw.lower()
    )
    if "{u}" in raw:
        text = raw.replace("{u}", target_mention)
    elif "{target}" in raw:
        text = raw.replace("{target}", target_mention)
    elif has_mention:
        text = raw
    else:
        text = f"{target_mention} {raw}"

    if not text.lstrip().startswith("#"):
        text = f"# {text}"

    parts = [text]
    if link:
        parts.append(link.strip())
    if gif:
        parts.append(gif.strip())

    content = "\n".join(parts)
    return content[:2000]


# ============================================================
# RAID LOOP
# ============================================================
async def _raid_loop(channel, channel_id):
    print(f"[RAID START] ch={channel_id}")

    count = 0

    try:
        while True:
            state = _ACTIVE_RAIDS.get(channel_id)
            if state is None:
                print(f"[RAID STOP] state bị xoá sau {count} câu")
                break
            if state.get("task") is None:
                print(f"[RAID STOP] task bị clear sau {count} câu")
                break

            target_mention = state.get("target_mention") or "<@0>"
            lines = state.get("lines") or _DEFAULT_LINES
            link = state.get("link") or ""
            gif = state.get("gif") or ""
            delay = state.get("delay") or 1.2

            try:
                raw = random.choice(lines)
            except Exception:
                raw = "sủa ít thôi"

            content = _build_content(raw, target_mention, link, gif)

            sent = False

            # === PRIMARY: channel.send() — PUBLIC ===
            try:
                await channel.send(
                    content,
                    allowed_mentions=discord.AllowedMentions(
                        everyone=True,
                        roles=True,
                        users=True,
                        replied_user=False,
                    ),
                )
                sent = True
                count += 1
                if count % 5 == 1:
                    print(f"[{time.strftime('%H:%M:%S')}] #{count} OK")

            except discord.HTTPException as e:
                if e.status == 429:
                    ra = float(getattr(e, "retry_after", 2.0) or 2.0)
                    print(f"[429] chờ {ra:.2f}s")
                    await asyncio.sleep(ra + 0.3)
                    continue
                elif e.status in (401, 403, 404):
                    print(f"[{e.status}] channel.send fail → fallback")
                else:
                    print(f"[ERR {e.status}] {getattr(e, 'text', str(e))[:120]}")
                    await asyncio.sleep(1.5)
                    continue

            except asyncio.CancelledError:
                raise

            except Exception as ex:
                print(f"[ERR] {type(ex).__name__}: {ex}")
                await asyncio.sleep(1.5)
                continue

            # === FALLBACK: interaction followup (public) ===
            if not sent:
                inter = state.get("interaction")
                if inter is None:
                    print("[STOP] channel.send fail + không có fallback")
                    break
                try:
                    await inter.followup.send(
                        content, ephemeral=False
                    )
                    sent = True
                    count += 1
                    if count % 5 == 1:
                        print(f"[{time.strftime('%H:%M:%S')}] #{count} OK (followup)")
                except discord.HTTPException as e2:
                    if e2.status == 429:
                        ra = float(getattr(e2, "retry_after", 2.0) or 2.0)
                        print(f"[429 fallback] chờ {ra:.2f}s")
                        await asyncio.sleep(ra + 0.3)
                        continue
                    elif e2.status in (401, 403, 404):
                        print(f"[{e2.status}] followup chết — tiếp tục thử channel.send")
                        await asyncio.sleep(3.0)
                        continue
                    else:
                        print(f"[ERR fallback {e2.status}]")
                        await asyncio.sleep(2.0)
                        continue
                except asyncio.CancelledError:
                    raise
                except Exception as e3:
                    print(f"[ERR fallback] {type(e3).__name__}: {e3}")
                    await asyncio.sleep(2.0)
                    continue

            # === Delay ===
            d = max(1.1, float(delay))
            await asyncio.sleep(random.uniform(d * 0.85, d * 1.15))

    except asyncio.CancelledError:
        print(f"[RAID CANCELLED] sau {count} câu")
        raise

    finally:
        st = _ACTIVE_RAIDS.get(channel_id)
        if st and st.get("task") is asyncio.current_task():
            st["task"] = None
        print(f"[RAID END] tổng {count} câu")


# ============================================================
# START / STOP
# ============================================================
def _start_raid(interaction, target_id, target_mention, channel_id, delay=None):
    st = _ensure_state(channel_id, target_id, target_mention)

    # Cancel task cũ nếu đang chạy
    old_task = st.get("task")
    if old_task and not old_task.done():
        try:
            old_task.cancel()
        except Exception:
            pass

    st["target_id"] = target_id
    st["target_mention"] = target_mention
    st["interaction"] = interaction
    if delay is not None:
        try:
            st["delay"] = max(1.1, float(delay))
        except Exception:
            pass

    channel = interaction.channel
    if channel is None:
        print("[START] channel None")
        return

    task = asyncio.create_task(_raid_loop(channel, channel_id))
    st["task"] = task


def _stop_raid(channel_id):
    st = _ACTIVE_RAIDS.get(channel_id)
    if not st:
        return False
    t = st.get("task")
    if t is None or t.done():
        st["task"] = None
        return False
    try:
        t.cancel()
    except Exception:
        pass
    st["task"] = None
    return True


# ============================================================
# MODAL — SET NỘI DUNG SPAM
# ============================================================
class SpamConfigModal(discord.ui.Modal, title="⚙️ SET NỘI DUNG SPAM"):
    content_text = discord.ui.TextInput(
        label="Nội dung (mỗi dòng 1 câu)",
        style=discord.TextStyle.paragraph,
        placeholder=(
            "Ví dụ:\n"
            "ngu vcl\n"
            "óc chó\n"
            "cút mẹ mày đi\n\n"
            "Không cần tag — bot tự tag user + tự làm chữ bự."
        ),
        required=False,
        max_length=1800,
    )
    link_text = discord.ui.TextInput(
        label="Link kèm theo (tuỳ chọn)",
        style=discord.TextStyle.short,
        placeholder="https://discord.gg/xxx",
        required=False,
        max_length=200,
    )
    gif_text = discord.ui.TextInput(
        label="URL ảnh/GIF (tuỳ chọn)",
        style=discord.TextStyle.short,
        placeholder="https://media.giphy.com/xxx.gif",
        required=False,
        max_length=300,
    )
    delay_text = discord.ui.TextInput(
        label="Delay (giây, min 1.1)",
        style=discord.TextStyle.short,
        placeholder="1.5",
        required=False,
        max_length=6,
    )

    def __init__(self, channel_id, target_id=None, target_mention=None):
        super().__init__()
        self.channel_id = channel_id
        self.target_id = target_id
        self.target_mention = target_mention

    async def on_submit(self, interaction: discord.Interaction):
        try:
            state = _ensure_state(
                self.channel_id, self.target_id, self.target_mention
            )

            raw = (self.content_text.value or "").strip()
            if raw:
                lines = [l.strip() for l in raw.split("\n") if l.strip()]
                if lines:
                    state["lines"] = lines

            link_v = (self.link_text.value or "").strip()
            gif_v = (self.gif_text.value or "").strip()
            state["link"] = link_v or None
            state["gif"] = gif_v or None

            try:
                if self.delay_text.value:
                    d = float(self.delay_text.value.replace(",", "."))
                    d = max(1.1, min(60.0, d))
                    state["delay"] = d
            except Exception:
                pass

            info = (
                f"✅ **ĐÃ SET**\n"
                f"• Pool: `{len(state['lines'])}` câu\n"
                f"• Link: `{'có' if state.get('link') else 'không'}`\n"
                f"• GIF: `{'có' if state.get('gif') else 'không'}`\n"
                f"• Delay: `{state['delay']:.2f}s`\n"
                f"-# Bot tự tag user + tự bự chữ. Bấm **🚀 Bật Auto Raid** để chạy."
            )
            await interaction.response.send_message(info, ephemeral=True)
        except Exception as e:
            print(f"[MODAL ERR] {e}")
            try:
                await interaction.response.send_message(
                    f"❌ Lỗi: `{str(e)[:150]}`", ephemeral=True)
            except Exception:
                pass


# ============================================================
# VIEW — PANEL (ephemeral, chỉ người gọi /chui thấy)
# ============================================================
class RaidMenuView(discord.ui.View):
    def __init__(self, target_id, target_mention, channel_id):
        super().__init__(timeout=None)
        self.target_id = target_id
        self.target_mention = target_mention
        self.channel_id = channel_id

    @discord.ui.button(
        label="Bật Auto Raid",
        style=discord.ButtonStyle.danger,
        emoji="🚀",
        custom_id="raid_on",
        row=0,
    )
    async def btn_on(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(thinking=False, ephemeral=True)
        except Exception:
            pass

        _start_raid(
            interaction,
            self.target_id,
            self.target_mention,
            self.channel_id,
            delay=None,
        )

        try:
            await interaction.followup.send(
                f"🚀 **ĐÃ KÍCH NỔ AUTORAID** lên đầu {self.target_mention}\n"
                f"-# Channel.send() — chạy mọi nơi, KHÔNG giới hạn câu.\n"
                f"-# Spam sẽ hiện **công khai** cho mọi người trong channel.",
                ephemeral=True,
            )
        except Exception:
            pass

    @discord.ui.button(
        label="Tắt Auto Raid",
        style=discord.ButtonStyle.secondary,
        emoji="🛑",
        custom_id="raid_off",
        row=0,
    )
    async def btn_off(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(thinking=False, ephemeral=True)
        except Exception:
            pass

        if _stop_raid(self.channel_id):
            try:
                await interaction.followup.send(
                    "🛑 **ĐÃ THU QUÂN.**", ephemeral=True)
            except Exception:
                pass
        else:
            try:
                await interaction.followup.send(
                    "❌ Không có luồng nào chạy!", ephemeral=True)
            except Exception:
                pass

    @discord.ui.button(
        label="Set nội dung spam",
        style=discord.ButtonStyle.primary,
        emoji="⚙️",
        custom_id="raid_set",
        row=0,
    )
    async def btn_set(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(
                SpamConfigModal(
                    self.channel_id, self.target_id, self.target_mention
                )
            )
        except Exception as e:
            print(f"[MODAL ERR] {e}")

    @discord.ui.button(
        label="Reset pool gốc",
        style=discord.ButtonStyle.secondary,
        emoji="♻️",
        custom_id="raid_reset",
        row=1,
    )
    async def btn_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(thinking=False, ephemeral=True)
        except Exception:
            pass
        state = _ACTIVE_RAIDS.get(self.channel_id)
        if state:
            state["lines"] = list(_DEFAULT_LINES)
            state["link"] = None
            state["gif"] = None
            state["delay"] = 1.2
            msg = f"♻️ Reset pool gốc ({len(_DEFAULT_LINES)} câu)."
        else:
            msg = "❌ Chưa bật raid."
        try:
            await interaction.followup.send(msg, ephemeral=True)
        except Exception:
            pass


# ============================================================
# /chui — PANEL EPHEMERAL
# ============================================================
@bot.tree.command(name="chui", description="Bảng điều khiển AutoRaid — spam mọi nơi")
@app_commands.describe(user="Nạn nhân")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.user_install()
async def s_chui(interaction: discord.Interaction, user: discord.User):
    try:
        if not await _check_perm(interaction):
            return
        if user.id in (bot.user.id, interaction.user.id):
            try:
                await interaction.response.send_message(
                    "Tự chửi chính mình à? 🤡", ephemeral=True)
            except Exception:
                pass
            return

        cid = interaction.channel_id
        mention = f"<@{user.id}>"

        # Dừng raid cũ (giữ config để panel có thể edit lại)
        _stop_raid(cid)

        # Đảm bảo state tồn tại — modal sẽ edit vào đây
        _ensure_state(cid, user.id, mention)

        # EPHEMERAL defer → panel chỉ mình người gọi thấy
        try:
            await interaction.response.defer(thinking=False, ephemeral=True)
        except Exception:
            pass

        view = RaidMenuView(
            target_id=user.id,
            target_mention=mention,
            channel_id=cid,
        )

        await interaction.followup.send(
            content=(
                f"⚔️ **CỖ MÁY HỦY DIỆT** khoá mục tiêu {mention}\n"
                f"🔥 **Bật Auto Raid** → spam `channel.send()`, chạy cả DM "
                f"lẫn guild, **vô hạn câu**.\n"
                f"⚙️ **Set nội dung** → đổi text/link/GIF. Bot tự tag + tự bự chữ.\n"
                f"-# Panel này CHỈ MÌNH BẠN THẤY. Spam vẫn hiện công khai."
            ),
            view=view,
            ephemeral=True,
        )
    except Exception as e:
        print(f"[LỖI /chui] {e}")


# ============================================================
# /say
# ============================================================
@bot.tree.command(name="say", description="Gửi tin nhắn (kèm link nếu muốn)")
@app_commands.describe(
    text="Nội dung",
    link_server="Link kèm theo",
    repeat="Số lần (1-50)",
    delay="Delay giữa các lần",
)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.user_install()
async def s_say(
    interaction: discord.Interaction,
    text: str,
    link_server: str = None,
    repeat: int = 1,
    delay: float = 1.2,
):
    try:
        if not await _check_perm(interaction):
            return

        try:
            await interaction.response.defer(thinking=False, ephemeral=True)
        except Exception:
            pass

        repeat = max(1, min(50, int(repeat)))
        delay = max(1.1, min(30.0, float(delay)))

        parts = [text[:1500]]
        if link_server:
            parts.append(f"📡 {link_server}")
        content = "\n\n".join(parts)

        channel = interaction.channel
        for i in range(repeat):
            try:
                await channel.send(
                    content,
                    allowed_mentions=discord.AllowedMentions(
                        everyone=True, roles=True, users=True),
                )
            except discord.HTTPException as e:
                if e.status == 429:
                    ra = float(getattr(e, "retry_after", 2.0) or 2.0)
                    await asyncio.sleep(ra + 0.3)
                else:
                    try:
                        await interaction.followup.send(content, ephemeral=False)
                    except Exception:
                        break
            except Exception:
                break
            if i < repeat - 1:
                await asyncio.sleep(random.uniform(delay * 0.85, delay * 1.15))
    except Exception as e:
        print(f"[LỖI /say] {e}")


# ============================================================
# /slap
# ============================================================
_SLAPS = [
    "vả cho {u} phát lệch mặt 🤚",
    "tát {u} rơi 3 cái răng 🦷",
    "bố vả {u} bay sang Lào 🛫",
    "tát {u} lệch cả hàm 🖐️",
    "vả {u} rụng răng hàm 🤜",
    "đấm {u} gãy mũi 👊",
    "đá {u} bay vào tường 🦵",
    "táng {u} lệch cổ 🤛",
]


@bot.tree.command(name="slap", description="Vả vào mõm thằng ất ơ")
@app_commands.describe(user="Nạn nhân")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.user_install()
async def s_slap(interaction: discord.Interaction, user: discord.User):
    try:
        if not await _check_perm(interaction):
            return
        try:
            await interaction.response.defer(thinking=False, ephemeral=True)
        except Exception:
            pass

        mention = f"<@{user.id}>"
        lines = [random.choice(_SLAPS).replace("{u}", mention) for _ in range(3)]
        content = "🖕 **Tát lệch mõm:**\n" + "\n".join(lines)

        try:
            await interaction.channel.send(content)
        except Exception:
            try:
                await interaction.followup.send(content, ephemeral=False)
            except Exception:
                pass
    except Exception as e:
        print(f"[LỖI /slap] {e}")


# ============================================================
# /spamset — SET NHANH CONFIG (không tự start)
# ============================================================
@bot.tree.command(name="spamset", description="Set nhanh nội dung spam (dùng /chui để bật)")
@app_commands.describe(
    target="Nạn nhân",
    text="Nội dung (mỗi dòng 1 câu, không cần tag)",
    link="Link kèm theo",
    gif="URL ảnh/GIF",
    delay="Delay (min 1.1)",
)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.user_install()
async def s_spamset(
    interaction: discord.Interaction,
    target: discord.User,
    text: str = None,
    link: str = None,
    gif: str = None,
    delay: float = 1.2,
):
    try:
        if not await _check_perm(interaction):
            return

        try:
            await interaction.response.defer(thinking=False, ephemeral=True)
        except Exception:
            pass

        cid = interaction.channel_id
        mention = f"<@{target.id}>"

        state = _ensure_state(cid, target.id, mention)

        if text:
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            if lines:
                state["lines"] = lines
        if link:
            state["link"] = link.strip()
        if gif:
            state["gif"] = gif.strip()
        try:
            state["delay"] = max(1.1, min(60.0, float(delay)))
        except Exception:
            pass
        state["target_id"] = target.id
        state["target_mention"] = mention

        await interaction.followup.send(
            f"✅ **Đã set config** cho {mention}\n"
            f"• Pool: `{len(state['lines'])}` câu\n"
            f"• Link: `{'có' if state.get('link') else 'không'}`\n"
            f"• GIF: `{'có' if state.get('gif') else 'không'}`\n"
            f"• Delay: `{state['delay']:.2f}s`\n"
            f"-# Bấm **/chui** → **🚀 Bật Auto Raid** để chạy",
            ephemeral=True,
        )
    except Exception as e:
        print(f"[LỖI /spamset] {e}")


# ============================================================
# RICH PRESENCE (/presence)
# ============================================================
_presence_owner_cache = {"id": None}


async def _presence_owner_id():
    if _presence_owner_cache["id"] is None:
        app = await bot.application_info()
        owner = app.team.owner if getattr(app, "team", None) else app.owner
        _presence_owner_cache["id"] = owner.id
    return _presence_owner_cache["id"]


@bot.tree.command(name="presence", description="Đổi Rich Presence trên profile của bạn")
@app_commands.describe(
    status="Dòng chữ to (VD: ĐANG XEM XXX)",
    note="Chú thích ảnh lớn",
    small="Chú thích ảnh nhỏ",
    anh="Gửi ảnh đính kèm để làm ảnh presence",
    reset="Trả mọi thứ về mặc định",
)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.user_install()
async def s_presence(
    interaction: discord.Interaction,
    status: str = None,
    note: str = None,
    small: str = None,
    anh: discord.Attachment = None,
    reset: bool = False,
):
    st = globals().get("PRESENCE_STATE")
    df = globals().get("PRESENCE_DEFAULTS")
    rf = globals().get("PRESENCE_REFRESH", 15)
    if st is None or df is None:
        return await interaction.response.send_message(
            "❌ presence.py chưa được load trong main.py.", ephemeral=True
        )
    try:
        owner_id = await _presence_owner_id()
    except Exception as e:
        return await interaction.response.send_message(
            f"❌ Không lấy được ID chủ bot: {e}", ephemeral=True
        )
    if interaction.user.id != owner_id:
        return await interaction.response.send_message(
            "❌ Chỉ chủ bot mới đổi được presence.", ephemeral=True
        )

    if reset:
        st.update(df)
        msg = "Đã reset presence về mặc định."
    else:
        changed = []
        if status is not None:
            st["details"] = status
            changed.append(f"status=`{status}`")
        if note is not None:
            st["large_text"] = note
            changed.append(f"note=`{note}`")
        if small is not None:
            st["small_text"] = small
            changed.append(f"small=`{small}`")
        if anh is not None:
            st["large_image"] = anh.url
            changed.append("ảnh=đính kèm")
        msg = ("Đã đổi: " + ", ".join(changed)) if changed else "Không đổi gì."
    msg += f"\n-# Áp dụng trong ~{rf}s."
    await interaction.response.send_message(msg, ephemeral=True)


# ============================================================
# SYNC
# ============================================================
async def sync_slash(guild_id=None):
    try:
        if guild_id:
            g = discord.Object(id=int(guild_id))
            bot.tree.copy_global_to(guild=g)
            return await bot.tree.sync(guild=g)
        return await bot.tree.sync()
    except Exception as e:
        print(f"[SYNC ERR] {e}")
        return []


try:
    if log:
        log.info("slash.py v71.2 — panel ephemeral, spam public, auto-tag + chữ bự")
except Exception:
    pass

print("[slash.py v71.2] loaded — panel riêng tư, spam công khai, auto-tag, chữ bự, everyone/here OK")