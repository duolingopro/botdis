# roast_vn.py — CHỬI VN CHÍNH GỐC v2.0
# Style: chợ búa · hàng xóm · mẹ chồng · bà bán cá · cà khịa
# Không có body ngoại hình — chỉ chửi kiểu VN đặc
# Mở - Thân - Kết, đậm chất VN

import random

_R = random


# ============================================================
# MỞ ĐẦU — CHÀO HỎI KIỂU VN
# ============================================================
_VN_MO = [
    # CHÀO CƠ BẢN
    "này {u} ơi là {u}",
    "con {u} ơi",
    "ái chà {u}",
    "ối dồi ôi {u}",
    "trời ơi là trời {u} à",
    "hỡi ơi {u}",
    "ê cái thằng {u} kia",
    "cái con {u} kia",
    "nghe đây {u}",
    "ông ơi là ông {u} ơi",
    "mở mồm ra nghe bố nói này {u}",
    "ngồi yên cho bố nói mấy câu {u}",
    "bố nói cho mà nghe hả {u}",
    "tao nói cho mày nghe nè {u}",
    "à {u} hả, quen mặt đấy",
    "lâu rồi không gặp {u}, mặt vẫn chai như ngày nào",
    "ai cho mày lên tiếng hả {u}",
    "con mẹ mày sinh ra mày mà không biết nhục hả {u}",
    "ê cưng, {u} đấy à",
    "sáng nay ăn gì mà dữ hả {u}",

    # CHÀO KIỂU HÀNG XÓM
    "này {u} ơi, mày hôm nay lại lên cơn à",
    "tưởng ai, hoá ra {u}",
    "ồ {u} hả, tưởng đi đâu mất tích ai ngờ ở đây",
    "tao lại tưởng con chó nào sủa, hoá ra {u}",
    "ơ {u} còn sống hả, tưởng chết đâu rồi",
    "{u} ơi, mẹ mày biết mày đang làm gì không",
    "kìa {u}, bố mày biết chưa",
    "{u} à, về nhà ăn cơm đi con",
    "{u} ơi, hàng xóm bảo mày hâm đấy",

    # CHÀO KIỂU BÀ BÁN CÁ
    "ối giời ơi là giời {u} à",
    "{u} ơi, có tin gì mới không con",
    "này cu {u}, lại đây bà bảo",
    "{u} à, bà kể cho mà nghe nè",
    "này {u}, mày biết chuyện gì chưa",
    "ơ cái con {u} này, tao chưa nói hết đã sủa",

    # CHÀO KIỂU BỐ ĐỜI
    "mày biết bố mày là ai không {u}",
    "{u} ơi, mày chưa đủ tuổi nói chuyện với bố đâu",
    "này {u}, bố nói câu cuối cho mà nghe",
    "{u} à, bố đéo rảnh tiếp mày lâu đâu",
    "{u}, mày có biết tôn ti trật tự không",
]


# ============================================================
# THÂN — CHỬI KIỂU VN
# ============================================================

# --- CHỢ BÚA — bà bán cá, hàng thịt, chợ Đồng Xuân ---
_VN_CHO = [
    "mày nói câu nào là tao nghe mùi cứt câu đó",
    "mày mở mồm ra là cả chợ phải bịt mũi",
    "cái mồm mày như cái loa phường, sủa đéo ai nghe",
    "mày nói dai như đỉa phải vôi, tao điếc cả tai",
    "mày sủa như chó dại ngoài chợ, đéo ai dám lại gần",
    "mày nói như bà hàng cá chợ Đồng Xuân, cãi đéo ai cãi lại",
    "mày cãi như bà bán thịt, miệng đéo ngớt lời",
    "mày sủa như con chó hoang đầu chợ, cắn bừa",
    "mày kêu như con mèo động đực đầu ngõ",
    "mày sủa dai như chó nhà hàng xóm, đéo ai đuổi cũng không thôi",
    "mày nói năng như bà hàng xóm, càm ràm cả ngày đéo hết chuyện",
    "mày ăn nói như cái chợ trời, đéo có trật tự gì",
    "mày nói nhảm như bà bán nước chè đầu làng",
    "mày sủa như mấy con chó bị nhốt trong chuồng",
    "mày nói năng vô duyên như bà bán ốc đầu hẻm",
    "mày mở mồm là người ta bịt mũi bỏ chạy",
    "mày nói xong người ta phải đi tắm rửa lại mồm",
    "mày nói nhảm như con vẹt học nói",
    "mày sủa loạn xạ như chó dại cắn chợ",
    "mày nói nhảm như bà đồng cốt, đéo ai tin",
]

# --- HÀNG XÓM — cà khịa, so bì, ghen tị ---
_VN_HX = [
    "mày làm được cái đéo gì nên hồn mà láo",
    "mày ăn cơm chưa mà sủa dữ vậy",
    "mày học lớp mấy rồi mà ăn nói vô học",
    "mày có biết chữ không mà lên mạng sủa",
    "mày đi chợ chưa mà hống hách",
    "mày đi làm chưa mà oai như chủ tịch",
    "mày có tiền chưa mà làm sang",
    "mày có chồng/vợ chưa mà dạy đời",
    "mày có con chưa mà nói chuyện gia đình",
    "mày có nhà chưa mà nói chuyện đất đai",
    "mày có xe chưa mà khoe",
    "mày lo cho bản thân đi, đéo lo được mà đi lo chuyện thiên hạ",
    "mày ăn gì mà ngu thế, ăn cơm với cứt à",
    "mày uống gì mà nói nhảm vậy, uống nhầm thuốc à",
    "mày ngủ đủ giấc chưa mà lú lẫn",
    "mày có bị bệnh gì không mà ăn nói vô duyên",
    "mày đi khám sức khỏe chưa, có vấn đề về đầu à",
    "mày bị đánh đập hồi nhỏ à mà nói năng vô học",
    "mày ở nhà có ai dạy mày không",
    "mày sinh ra trong chuồng chó à",
    "mày lớn lên trong cống rãnh à",
    "mày thất học hả, hay trốn học cả đời",
    "mày bỏ học từ cấp 1 hả mà dốt thế",
    "mày nói câu nào là bố mẹ mày ở nhà phải xin lỗi câu đó",
    "mày nói câu nào là tổ tiên mày phải chui xuống đất",
    "mày đại diện cho cả dòng họ mày à, nhục vcl",
    "mày làm cả họ nhà mày xấu hổ đấy biết không",
    "mày thua cả con chó nhà hàng xóm về độ hiểu biết",
    "mày thua cả con gà nhà tao về độ thông minh",
    "mày thua cả con mèo hoang về độ khôn",
    "mày còn thua cả cái cây trước nhà vì cây còn biết đứng im",
    "mày làm được cái gì cho đời rồi",
    "mày ăn hại cả đời, đéo làm được tích sự gì",
    "mày sống trên đời này để làm gì hả",
    "mày sống có ích gì cho gia đình không",
    "mày sống có ích gì cho xã hội không",
    "mày có ai cần mày không mà lên mặt",
    "mày có ai yêu mày không mà sống",
    "mày có ai thương mày không mà cà khịa",
]

# --- MẸ CHỒNG — khó tính, soi mói, chê bai ---
_VN_MC = [
    "mày ăn ở thế nào mà đéo ai thèm",
    "mày ăn ở thế nào mà con chó nó cũng khinh",
    "mày ăn ở thế nào mà hàng xóm đéo ai chào",
    "mày ăn ở thế nào mà bạn bè nó bỏ đi hết",
    "mày ăn ở thế nào mà người yêu nó đá mày",
    "mày ăn ở thế nào mà vợ/chồng nó khổ",
    "mày ăn ở thế nào mà con cái nó bỏ",
    "mày làm gì nên hồn chưa mà oai",
    "mày lo được cho bố mẹ chưa mà nói chuyện người lớn",
    "mày nuôi được vợ con chưa mà lên giọng",
    "mày có nhà cửa gì chưa mà chê người khác",
    "mày có sự nghiệp gì chưa mà khinh người",
    "mày thử nhìn lại bản thân trước khi nói người khác",
    "mày nhìn gương đi rồi hãy mở miệng",
    "mày tự thấy nhục chưa khi nói những lời đó",
    "mày có biết xấu hổ không hay quên rồi",
    "mày không biết nhục à, hay nhục đéo ai bằng",
    "mày đéo có liêm sỉ à mà ăn nói thế",
    "mày đéo có tự trọng à, sống nhục thế",
    "mày đéo có giáo dục à, ăn nói vô học",
    "mày đéo có dạy dỗ à, nói năng hỗn láo",
    "mày đéo có văn hoá à, nói chuyện vô duyên",
    "mày đéo có hiểu biết à, nói câu nào ngu câu đó",
    "mày đéo có đầu à, sao nghĩ toàn chuyện ngu",
    "mày về mà học lại cái đã",
    "mày về mà hỏi bố mẹ mày đi",
    "mày về mà xin lỗi tổ tiên mày đi",
    "mày về mà tự kỷ lại đi con",
]

# --- CÀ KHỊA — châm chọc, khiêu khích ---
_VN_CK = [
    "mày tưởng mày là ai mà to mồm",
    "mày tưởng mày là cái gì của thiên hạ à",
    "mày tưởng mày là ông nội người ta à",
    "mày tưởng mày là tổng thống à mà ra lệnh",
    "mày tưởng mày là chủ tịch à mà lên mặt",
    "mày tưởng mày là bố thiên hạ à",
    "mày tưởng mày ngon lắm à",
    "mày tưởng mày giỏi lắm à",
    "mày tưởng mày khôn lắm à",
    "mày tưởng mày đẹp trai/xinh gái lắm à",
    "mày tưởng mày giàu lắm à",
    "mày tưởng mày quyền lực lắm à",
    "mày tưởng mày có tiếng nói lắm à",
    "mày tưởng mày đéo ai sánh bằng à",
    "mày tưởng mày hoàn hảo lắm à",
    "mày có cái đéo gì mà lên mặt",
    "mày có cái đéo gì mà oai",
    "mày có cái đéo gì mà khoe",
    "mày có gì hơn người khác không mà chê",
    "mày có gì đặc biệt không mà lên giọng",
    "mày làm được gì cho đời chưa mà nói",
    "mày có công lao gì chưa mà đòi hỏi",
    "mày có đóng góp gì chưa mà lên mặt",
    "mày là cái thá gì mà dạy đời người khác",
    "mày là cái thá gì mà phán xét",
    "mày là cái thá gì mà chỉ trích",
    "mày là cái thá gì mà đòi hỏi",
    "mày là cái thá gì mà to mồm",
    "mày là cái thá gì mà lên giọng",
    "mày là cái thá gì mà dạy bảo",
]

# --- CHỬI NHÀ — bố mẹ, tổ tiên, dòng họ ---
_VN_NHA = [
    "bố mẹ mày dạy mày thế à",
    "bố mẹ mày không dạy mày à",
    "bố mẹ mày biết mày ăn nói thế này chưa",
    "bố mẹ mày mà biết chắc chết vì nhục",
    "bố mẹ mày mà nghe chắc phải xin lỗi hàng xóm",
    "bố mẹ mày sinh ra mày chắc đêm đó trời mưa bão",
    "bố mẹ mày đẻ mày ra chắc lúc đó say rượu",
    "ông bà mày ở dưới suối vàng nghe mày nói chắc phải trùm chăn",
    "tổ tiên 18 đời nhà mày chắc phải chui lên xin lỗi",
    "dòng họ mày có mày chắc phải ghi vào sách đen",
    "mẹ mày mà nhìn thấy mày bây giờ chắc đi xét nghiệm ADN",
    "bố mày mà nhìn thấy mày bây giờ chắc đi nhậu 3 ngày",
    "anh chị em nhà mày mà biết chắc xấu hổ với họ hàng",
    "ông già mày chắc phải đội mồ sống dậy dạy mày",
    "bà nội mày chắc thương mày lắm, thương đến mức không dám nhìn",
    "mày là nỗi nhục của cả dòng họ",
    "mày làm cả dòng họ phải đổi tên",
    "mày làm bố mẹ mày phải chuyển nhà",
    "mày làm ông bà mày phải xin lỗi tổ tiên",
    "mày làm cả gia đình mày phải sống trong nhục",
    "mày đéo xứng làm con của bố mẹ mày",
    "mày đéo xứng làm cháu của ông bà mày",
    "mày đéo xứng mang họ của dòng tộc",
    "mày đéo xứng làm người trong gia đình",
    "mày là cục nợ của bố mẹ mày",
    "mày là gánh nặng của gia đình",
    "mày là tai họa của dòng họ",
    "mày là ung nhọt của tổ tiên",
    "mày là vết nhơ của cả gia đình",
    "mày sinh ra chỉ để làm khổ bố mẹ",
    "mày sinh ra chỉ để làm nhục dòng họ",
    "mày sinh ra là sai lầm của tạo hóa",
    "mày sinh ra là bug của tự nhiên",
]

# --- TỰ KỶ / LOSER — cô đơn, thất bại ---
_VN_LOSER = [
    "mày loser tới mức đéo ai buồn block",
    "mày cô đơn tới mức phải nói chuyện với gương",
    "mày cô đơn tới mức con mèo cũng đéo thèm",
    "mày cô đơn tới mức tường phải tự né",
    "mày đéo có bạn bè thật, chỉ có clone tự vuốt",
    "mày đéo có ai yêu, đéo có ai thương",
    "mày đéo có ai nhớ, đéo có ai quan tâm",
    "mày bị người yêu đá vì đéo có tiền",
    "mày bị người yêu bỏ vì quá dở hơi",
    "mày bị bạn bè xa lánh vì tính xấu",
    "mày bị họ hàng đéo thèm nhìn mặt",
    "mày bị làng xóm đéo thèm chào",
    "mày bị cả xã hội đéo thèm tiếp",
    "mày thất nghiệp dài hạn, ăn bám bố mẹ",
    "mày đi làm 10 năm đéo có đồng tiết kiệm",
    "mày nghèo rớt mùng tơi, đéo có nổi bộ đồ tử tế",
    "mày nợ ngập đầu, chủ nợ đuổi như đuổi tà",
    "mày ở nhà thuê cả đời, đéo mua nổi căn nhà",
    "mày đéo có tương lai, chỉ có bàn phím với mì tôm",
    "mày sống lay lắt như ký sinh trùng",
    "mày sống qua ngày, đéo có mục đích",
    "mày sống đéo có ý nghĩa gì",
    "mày sống chỉ để làm nhục gia đình",
    "mày sống chỉ để tốn cơm",
    "mày sống chỉ để tốn oxy",
    "mày sống chỉ để làm người khác chửi",
]


# ============================================================
# KẾT — BYE KIỂU VN
# ============================================================
_VN_KET = [
    "đấy, bố nói thế thôi, liệu hồn mà sửa",
    "bố đéo thèm nói nữa, mày tự ngẫm đi",
    "nói 3 câu thôi đủ rồi, thêm nữa tao đau đầu",
    "cút xa tầm mắt bố, đừng để bố nhắc lần 2",
    "thôi bố đi ngủ, chúc mày ngủ ngon",
    "sáng mai thức dậy đỡ ngu đi con",
    "bố nói thế là còn nhẹ, động vào bố lần nữa xem",
    "mày về soi gương đi, rồi tự thấy nhục",
    "bố đéo rảnh tiếp mày, đi chỗ khác mà sủa",
    "ăn cơm xong mà nghe mày nói chắc tao ói cả cơm",
    "bố khuyên mày đi khám não gấp trước khi quá muộn",
    "về mà hỏi mẹ mày xem mày sai ở đâu",
    "về mà xin lỗi tổ tiên mày đi",
    "về mà học lại cách ăn nói đi",
    "về mà tu tỉnh lại, đừng để bố phải dạy lần nữa",
    "thôi tao đi đây, mày ở lại mà tự kỷ",
    "tao đi chợ đây, mày ở nhà mà sủa tiếp",
    "tao đéo phí thời gian với loại như mày nữa",
    "bye con, nhớ sửa tính đi không sau này khổ",
    "bố chấm hết, mày tự lo thân đi",
    "cút mẹ mày đi cho bố nhờ",
    "biến mẹ mày đi cho bố nhờ",
    "im mẹ mồm lại cho bố nhờ",
    "sủa ít thôi cho đời nó nhờ",
    "ngậm mồm vào cho người ta nhờ",
    "tắt điện đi cho xã hội nhờ",
    "off mẹ đi cho cả làng nhờ",
]


# ============================================================
# TỪ ĐỆM — CHÈN GIỮA CÁC CÂU
# ============================================================
_VN_CHEN = [
    "à mà",
    "nói đến đây",
    "ấy chà",
    "mà này",
    "còn nữa",
    "chưa hết đâu",
    "à quên",
    "tiện thể",
    "một điều nữa",
    "đấy chưa kể",
    "thêm cái nữa",
    "và bố nói luôn",
    "nói thẳng ra",
    "thật ra thì",
    "mà thôi",
    "chốt lại",
    "tóm lại",
    "nói chung là",
    "à đấy",
    "ừm",
]


# ============================================================
# HÀM CHÍNH — FORGE ROAST VN
# ============================================================
_STYLES = ["ngan", "dai", "lan_man", "toi_da"]
_POOLS = [_VN_CHO, _VN_HX, _VN_MC, _VN_CK, _VN_NHA, _VN_LOSER]


def forge_roast_vn(target, style="dai"):
    """
    Chửi kiểu VN chính gốc.
    style:
      - ngan   : 1-2 câu, ngắn gọn
      - dai    : 4-6 câu
      - lan_man: 8-12 câu, dài dòng, có từ đệm
      - toi_da : 12-18 câu, full combo
    """
    if not target:
        target = "mày"
    target = str(target)[:80].strip() or "mày"

    # Cấu hình theo style
    if style == "ngan":
        n_mo = 1
        n_than = 1
        n_ket = 1
        chen_rate = 0.0
    elif style == "dai":
        n_mo = 1
        n_than = _R.randint(3, 5)
        n_ket = 1
        chen_rate = 0.2
    elif style == "lan_man":
        n_mo = _R.randint(1, 2)
        n_than = _R.randint(6, 9)
        n_ket = 1
        chen_rate = 0.35
    else:  # toi_da
        n_mo = _R.randint(2, 3)
        n_than = _R.randint(10, 15)
        n_ket = 1
        chen_rate = 0.4

    parts = []

    # --- MỞ ---
    used_mo = set()
    for _ in range(n_mo * 3):
        if len(used_mo) >= n_mo:
            break
        mo = _R.choice(_VN_MO).format(u=target)
        if mo not in used_mo:
            used_mo.add(mo)
            parts.append(mo)

    # --- THÂN ---
    pools_shuffled = _POOLS[:]
    _R.shuffle(pools_shuffled)

    used = set()
    count = 0
    for pool in pools_shuffled * 3:
        if count >= n_than:
            break
        line = _R.choice(pool)
        if line in used:
            continue
        used.add(line)
        parts.append(line)
        count += 1

    # --- KẾT ---
    parts.append(_R.choice(_VN_KET))

    # --- TRỘN TỪ ĐỆM ---
    if chen_rate > 0 and len(parts) > 3:
        for i in range(1, len(parts) - 1):
            if _R.random() < chen_rate:
                chen = _R.choice(_VN_CHEN)
                if not parts[i].startswith(chen):
                    parts[i] = f"{chen}, {parts[i]}"

    # --- GHÉP CÂU ---
    if parts and parts[0]:
        parts[0] = parts[0][0].upper() + parts[0][1:]

    out = ". ".join(parts)

    r = _R.random()
    if r < 0.3:
        out = out.replace(". ", "! ", 1)
    elif r < 0.5:
        out = out.replace(". ", "... ", 1)
    elif r < 0.7:
        out = out.replace(". ", "! ", 2)

    emoji = _R.choice([
        "", "", "", "",
        " 🤡", " 💀", " 😂", " 🤮", " 🐕", " 🚪", " ☠️", " 🤚", " 👋",
        " 🐖", " 💩", " 🗑️", " 😭", " 🐸", " 🌚", " 😤"
    ])
    out = out + emoji

    return out[:1900]


def forge_roast_vn_combo(target, lines=8):
    """Combo nhiều câu, mỗi câu 1 dòng riêng."""
    if not target:
        target = "mày"
    target = str(target)[:80].strip() or "mày"

    lines = max(3, min(20, lines))
    out = []
    used = set()

    mo = _R.choice(_VN_MO).format(u=target)
    out.append(mo)
    used.add(mo)

    pools_shuffled = _POOLS[:]
    _R.shuffle(pools_shuffled)
    count = 0
    for pool in pools_shuffled * 3:
        if count >= lines - 2:
            break
        line = _R.choice(pool)
        if line in used:
            continue
        used.add(line)
        out.append(line)
        count += 1

    out.append(_R.choice(_VN_KET))

    if out[0]:
        out[0] = out[0][0].upper() + out[0][1:]

    return "\n".join(out)[:1900]


log.info("roast_vn.py v2.0 — CHỬI VN CHÍNH GỐC loaded")