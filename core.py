"""MHXX RNG core logic, ported from mhxx-rng.ipynb (https://github.com/apmnnn/mhxx-rng)"""

# Default seed
DEFAULT_SEED = [0x0194FD72, 0x79E6C985, 0x08DD9701, 0x41CFCE91]

# Global state
s = list(DEFAULT_SEED)
x = y = z = w = t = f = 0
r0 = r1 = r2 = r3 = r4 = r5 = r6 = 0

skill1 = []
sp1 = []
skill2 = []
sp2 = []
slotvalue = []
th = 0
kind = 0

skill = []
origin = []
kinds = []
melding = []
kind_width = ''
noskill = ''
skill_width = ''


def set_seed(seed_list):
    global s
    s = list(seed_list)


def set_blue():
    global skill1, sp1, skill2, sp2, slotvalue, th, kind
    skill1 = [4,5,10,11,14,15,25,31,32,35,36,37,38,39,40,41,42,44,45,47,48,49,50,64,65,66,68,70,71,72,73,76,77,78,79,80,81,82,83,84,85,86,87,90,92,93,94,95,97,99,100,101,106,107,108,109,114,115,116,122,123,132]
    sp1 = [(3,7),(5,10),(3,7),(3,7),(3,7),(5,10),(3,7),(3,7),(3,7),(3,7),(3,7),(1,5),(2,6),(1,5),(1,5),(5,10),(5,10),(3,7),(2,6),(2,6),(2,6),(2,6),(2,6),(1,5),(1,5),(1,5),(3,7),(2,6),(1,5),(2,6),(2,6),(2,6),(2,6),(3,7),(3,7),(2,6),(2,6),(2,6),(1,5),(3,7),(3,7),(5,10),(5,10),(2,6),(2,6),(1,5),(1,5),(1,5),(2,6),(2,6),(2,6),(1,5),(2,6),(1,5),(3,7),(3,7),(3,7),(1,5),(3,7),(2,6),(3,7),(3,7)]
    skill2 = [4,5,17,18,25,26,27,28,29,30,32,33,34,35,36,37,39,40,41,43,44,45,47,48,49,50,64,65,66,68,69,70,71,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,99,100,101,105,106,107,108,109,114,115,116,119,122,123,125,132,134,135,136,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178]
    sp2 = [(3,5),(5,7),(7,10),(5,13),(5,7),(5,13),(5,13),(5,13),(5,13),(5,13),(5,7),(7,10),(3,5),(5,7),(5,7),(3,5),(5,5),(2,8),(5,7),(3,3),(5,7),(5,7),(3,5),(3,5),(3,5),(3,5),(3,5),(3,5),(3,5),(5,7),(7,10),(3,5),(1,3),(3,5),(3,3),(3,5),(3,5),(3,5),(3,5),(3,5),(3,5),(3,5),(1,3),(3,5),(3,5),(7,10),(7,10),(5,10),(5,10),(3,5),(5,10),(3,5),(1,3),(1,3),(1,3),(3,3),(3,5),(3,5),(3,5),(1,3),(7,10),(3,5),(1,3),(5,7),(5,7),(7,10),(1,3),(3,5),(5,12),(3,5),(5,7),(3,5),(7,10),(5,7),(3,5),(5,7),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3)]
    slotvalue = [(100,100,100),(3,53,88),(5,55,89),(7,57,89),(13,58,89),(16,60,90),(22,62,90),(30,66,90),(38,68,91),(50,72,91),(55,75,92),(59,77,92),(64,81,94),(67,83,94),(71,86,96),(74,88,96),(79,91,98),(82,92,98),(86,94,99),(90,96,99)]
    th = 15
    kind = 0


def set_red():
    global skill1, sp1, skill2, sp2, slotvalue, th, kind
    skill1 = [4,5,10,11,14,15,25,26,27,28,29,30,31,32,35,36,38,41,42,44,45,47,48,49,50,65,68,70,72,73,76,77,78,79,81,82,84,85,86,87,90,92,97,99,100,103,104,106,108,109,114,116,122,123,124,132]
    sp1 = [(1,5),(1,5),(1,5),(1,5),(1,5),(1,8),(1,5),(1,7),(1,7),(1,7),(1,7),(1,7),(1,5),(1,6),(1,5),(1,5),(1,6),(1,6),(1,6),(1,6),(1,5),(1,5),(1,5),(1,5),(1,5),(1,3),(1,5),(1,5),(1,5),(1,5),(1,5),(1,5),(1,6),(1,6),(1,6),(1,6),(1,6),(1,6),(1,6),(1,6),(1,5),(1,6),(1,6),(1,5),(1,5),(1,7),(1,7),(1,5),(1,5),(1,6),(1,7),(1,6),(1,5),(1,5),(1,5),(1,7)]
    skill2 = [3,4,5,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,33,34,35,36,37,39,40,41,42,44,45,47,48,49,50,64,65,66,68,69,70,71,74,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,97,99,100,101,103,104,105,106,107,108,109,110,114,115,116,117,119,120,122,123,124,125,132,134,135,136,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160]
    sp2 = [(10,13),(3,3),(10,3),(10,10),(10,10),(10,13),(10,13),(10,13),(10,13),(10,13),(10,13),(3,3),(10,13),(10,13),(10,13),(10,13),(10,13),(10,4),(10,8),(5,5),(3,3),(3,3),(3,3),(3,3),(5,8),(10,4),(3,3),(3,4),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(5,5),(3,3),(5,5),(10,10),(3,3),(3,3),(3,3),(3,3),(3,3),(3,4),(3,4),(5,5),(3,4),(3,4),(3,3),(3,4),(3,4),(3,4),(3,4),(10,10),(10,10),(3,3),(10,10),(3,4),(3,3),(3,3),(3,3),(3,4),(5,5),(5,5),(3,3),(10,10),(10,10),(5,5),(5,5),(3,3),(5,5),(3,3),(10,12),(10,9),(3,3),(3,4),(10,12),(10,12),(10,10),(3,3),(5,5),(5,5),(3,3),(8,10),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3),(3,3)]
    slotvalue = [(8,58,88),(9,59,88),(16,61,89),(17,62,89),(23,63,89),(25,65,90),(31,66,90),(38,68,90),(45,71,91),(58,76,91),(63,79,92),(66,80,92),(71,83,94),(74,84,94),(78,87,96),(82,90,96),(86,93,98),(88,94,98),(91,96,99),(94,97,99)]
    th = 25
    kind = 1


def set_yellow():
    global skill1, sp1, skill2, sp2, slotvalue, th, kind
    skill1 = [0,1,2,3,5,6,7,13,17,18,19,20,21,22,23,24,26,27,28,29,30,32,33,38,41,44,46,51,52,53,54,55,62,63,68,69,72,73,78,79,81,84,85,86,87,88,89,91,97,98,99,100,103,104,106,108,109,110,113,114,116,117,119,120,122,123,124,126,129,131,132]
    sp1 = [(1,5),(1,5),(1,5),(1,8),(1,4),(1,7),(1,7),(1,7),(1,4),(1,4),(1,8),(1,6),(1,6),(1,6),(1,6),(1,6),(1,7),(1,7),(1,7),(1,7),(1,7),(1,4),(1,4),(1,4),(1,6),(1,4),(1,6),(1,6),(1,10),(1,10),(1,10),(1,10),(1,10),(1,10),(1,3),(1,4),(1,3),(1,3),(1,6),(1,6),(1,6),(1,6),(1,4),(1,6),(1,6),(1,6),(1,6),(1,6),(1,6),(1,5),(1,3),(1,3),(1,5),(1,5),(1,3),(1,3),(1,6),(1,8),(1,8),(1,7),(1,6),(1,7),(1,8),(1,8),(1,4),(1,3),(1,3),(1,8),(1,8),(1,8),(1,3)]
    skill2 = [0,1,2,3,6,7,8,9,12,13,14,15,16,17,18,19,20,21,22,23,24,32,40,46,51,52,53,54,55,56,57,58,59,60,61,62,63,65,67,68,69,72,73,88,89,91,98,99,100,102,103,104,105,106,108,110,111,112,113,117,118,119,120,121,123,124,126,127,128,129,130,131,132,133]
    sp2 = [(10,7),(10,7),(10,7),(10,10),(10,8),(10,8),(10,10),(10,10),(10,10),(10,8),(5,5),(5,5),(10,10),(7,7),(7,7),(10,10),(10,10),(10,10),(10,10),(10,10),(10,10),(4,4),(5,5),(10,10),(8,8),(10,10),(10,10),(10,10),(10,10),(10,10),(10,10),(10,10),(10,12),(10,12),(10,10),(10,10),(10,10),(3,3),(10,10),(5,5),(7,7),(5,5),(5,5),(8,8),(8,8),(8,8),(5,5),(5,5),(5,5),(10,10),(7,7),(7,7),(8,8),(5,5),(5,5),(10,10),(10,10),(10,10),(10,10),(4,4),(10,10),(10,10),(10,10),(10,13),(5,5),(5,5),(10,10),(10,13),(10,10),(10,10),(10,13),(10,10),(5,5),(10,13)]
    slotvalue = [(2,72,100),(9,74,100),(16,76,100),(23,78,100),(30,80,100),(37,82,100),(44,84,100),(51,86,100),(58,88,100),(75,90,100),(83,92,100),(87,95,100),(90,97,100),(92,98,100),(94,99,100),(95,99,100),(97,100,100),(98,100,100),(99,100,100),(99,100,100)]
    th = 35
    kind = 2


def set_white():
    global skill1, sp1, skill2, sp2, slotvalue, th, kind
    skill1 = [0,1,2,3,6,7,8,9,12,13,14,16,17,18,19,20,21,22,23,24,46,51,52,53,54,55,56,57,58,59,60,61,62,63,67,69,88,89,91,98,102,103,104,105,110,111,112,113,118,119,120,121,126,127,128,129,130,131,133]
    sp1 = [(1,5),(1,5),(1,5),(1,8),(1,7),(1,7),(1,10),(1,10),(1,10),(1,7),(1,3),(1,5),(1,4),(1,4),(1,8),(1,6),(1,6),(1,6),(1,6),(1,6),(1,6),(1,8),(1,8),(1,8),(1,8),(1,8),(1,8),(1,8),(1,8),(1,8),(1,8),(1,8),(1,8),(1,8),(1,5),(1,4),(1,6),(1,6),(1,6),(1,4),(1,8),(1,3),(1,3),(1,10),(1,8),(1,8),(1,8),(1,8),(1,8),(1,8),(1,8),(1,10),(1,8),(1,10),(1,8),(1,8),(1,10),(1,8),(1,10)]
    skill2 = [0]
    sp2 = [(10,7)]
    slotvalue = [(55,100,100),(60,100,100),(65,100,100),(70,100,100),(75,100,100),(80,100,100),(85,100,100),(90,100,100),(95,100,100),(99,100,100),(100,100,100),(100,100,100),(100,100,100),(100,100,100),(100,100,100),(100,100,100),(100,100,100),(100,100,100),(100,100,100),(100,100,100)]
    th = 100
    kind = 3


def set_ja():
    global skill, origin, kinds, melding, kind_width, noskill, skill_width
    skill = ['毒　','麻痺','睡眠','気絶','聴覚','風圧','耐震','だる','耐暑','耐寒','寒冷','炎熱','盗み','対防','狂撃','細菌','裂傷','攻撃','防御','体力','火耐','水耐','雷耐','氷耐','龍耐','属耐','火攻','水攻','雷攻','氷攻','龍攻','属攻','特攻','研師','匠　','斬味','剣術','研磨','鈍器','抜会','抜減','納刀','納研','刃鱗','装速','反動','精密','通強','貫強','散強','重強','通追','貫追','散追','榴追','拡追','毒追','麻追','睡追','強追','属追','接追','減追','爆追','速射','射法','装数','変則','弾節','達人','痛撃','連撃','特会','属会','会心','裏会','溜短','スタ','体術','気力','走行','回性','回距','泡沫','ガ性','ガ強','ＫＯ','減攻','笛　','砲術','重撃','爆弾','本気','闘魂','無傷','チャ','龍気','底力','逆境','逆上','窮地','根性','気配','采配','号令','乗り','跳躍','無心','我慢','ＳＰ','千里','観察','狩人','運搬','加護','英雄','回量','回速','効果','広域','腹減','食い','食事','節食','肉食','茸食','野草','調成','調数','高速','採取','ハチ','護石','気ま','運気','剥取','捕獲','ベル','ココ','ポッ','ユク','龍識','飛行','紅兜','大雪','矛砕','岩穿','紫毒','宝纏','白疾','隻眼','黒炎','金雷','荒鉤','燼滅','朧隠','鎧裂','天眼','青電','銀嶺','鏖魔','真紅','真大','真矛','真岩','真紫','真宝','真白','真隻','真黒','真金','真荒','真燼','真朧','真鎧','真天','真青','真銀','真鏖','北辰','斬術','食欲','職工','剛腕','祈願','裏稼','刀匠','射手','状態','怒　','回術','居合','頑強','剛撃','盾持','潔癖','増幅','護収','強欲','対鋼','対霞','対炎','胴倍','秘術','護強']
    origin = ['マカ','炭鉱']
    kinds = ['風化したお守り','古びたお守り','光るお守り','なぞのお守り']
    melding = ['マカフシギ','天運']
    kind_width = '　<7'
    noskill = '◯◯----'
    skill_width = '　<2'


def set_en():
    global skill, origin, kinds, melding, kind_width, noskill, skill_width
    skill = ['Poison','Paralysis','Sleep','Stun','Hearing','Wind Res','Tremor Res','Bind Res','Heat Res','Cold Res','ColdBlooded','HotBlooded','Anti-Theft','Def Lock','Frenzy Res','Biology','Bleeding','Attack','Defense','Health','Fire Res','Water Res','Thunder Res','Ice Res','Dragon Res','Blight Res','Fire Atk','Water Atk','Thunder Atk','Ice Atk','Dragon Atk','Elemental','Status','Sharpener','Handicraft','Sharpness','Fencing','Grinder','Blunt','Crit Draw','Punish Draw','Sheathing','Sheathe Sharpen','Bladescale','Reaload Spd','Recoil','Precision','Normal Up','Pierce Up','Pellet Up','Heavy Up','Normal S+','Pierce S+','Pellet S+','Crag S+','Clust S+','Poison C+','Para C+','Sleep C+','Power C+','Elem C+','C.Range C+','Exhaust C+','Blast C+','Rapid Fire','Dead Eye','Loading','Haphazard','Ammo Saver','Expert','Tenderizer','Chain Crit','Crit Status','Crit Element','Critical Up','Negative Crit','FastCharge','Stamina','Constitution','Stam Recov','Distance Runner','Evasion','Evade Dist','Bubble','Guard','Guard Up','KO','Stam Drain','Maestro','Artillery','Destroyer','Bomb Boost','Gloves Off','Spirit','Unscathed','Chance','Dragon Spirit','Potential','Survivor','Furor','Crisis','Guts','Sense','Team Player','TeamLeader','Mounting','Vault','Insight','Endurance','Prolong SP','Psychic','Perception','Ranger','Transporter','Protection','Hero Shield','Rec Level','Rec Speed','Lasting Pwr','Wide-Range','Hunger','Gluttony','Eating','Light Eater','Carnivore','Mycology','Botany','Combo Rate','Combo Plus','Speed Setup','Gathering','Honey','Charmer','Whim','Fate','Carving','Capturer','Bherna','Kokoto','Pokke','Yukumo','Soaratorium','Flying Pub','Redhelm','Snowbaron','Stonefist','Drilltusk','Dreadqueen','C.beard','Silverwind','Deadeye','Dreadking','Thunderlord','Grimclaw','Hellblade','Nightcloak','Rustrazor','Soulseer','Boltreaver','Elderfrost','Bloodbath','Redhelm X','Snowbaron X','Stonefist X','Drilltusk X','Dreadqueen X','Crystalbeard X','Silverwind X','Deadeye X','Dreadking X','Thunderlord X','Grimclaw X','Hellblade X','Nightcloak X','Rustrazor X','Soulseer X','Boltreaver X','Elderfrost X','Bloodbath X','D. Fencing','Edge Lore','PowerEater','Mechanic','Brawn','Prayer','Covert','Edgemaster','SteadyHand','Status Res','Fury','Nimbleness','Readiness','Resilience','Brutality','Stalwart','Prudence','Amplify','Hoarding','Avarice','Anti-Kushala','Anti-Chameleos','Anti-Teostra','Torso Up','Secret Arts','Talisman Boost']
    origin = ['Melding','Quest']
    kinds = ['Enduring Charm','Timeworn Charm','Shining Charm','Mystery Charm']
    melding = ['Juju','Halcyon']
    kind_width = ' <14'
    noskill = ' ' * 15 + '----'
    skill_width = ' <15'


def init():
    global x, y, z, w, t, f
    x, y, z, w = s
    t = 0x0
    f = 0


def ascend():
    global x, y, z, w, t, f
    t = (x ^ (x << 15)) & 0xFFFFFFFF
    x = y
    y = z
    z = w
    w = w ^ (w >> 21) ^ t ^ (t >> 4)
    f += 1


def descend():
    global x, y, z, w, t, f
    t = w ^ z ^ (z >> 21)
    t ^= t >> 4
    t ^= t >> 8
    t ^= t >> 16
    w = z
    z = y
    y = x
    x = (t ^ (t << 15) ^ (t << 30)) & 0xFFFFFFFF
    f -= 1


def roll():
    global r0, r1, r2, r3, r4, r5, r6
    r0, r1, r2, r3, r4, r5, r6 = r1, r2, r3, r4, r5, r6, w
    ascend()


def poly_mul(p1, p2):
    res = 0
    while p2 > 0:
        if p2 & 1:
            res ^= p1
        p1 <<= 1
        p2 >>= 1
    return res


def poly_mod(p, m):
    m_len = m.bit_length()
    while (p.bit_length() - m_len) >= 0:
        delta_deg = p.bit_length() - m_len
        p ^= m << delta_deg
    return p


def poly_pow_mod(base, exp, mod):
    res = 1
    base = poly_mod(base, mod)
    while exp > 0:
        if exp & 1:
            res = poly_mod(poly_mul(res, base), mod)
        base = poly_mod(poly_mul(base, base), mod)
        exp >>= 1
    return res


def jump(frame):
    global x, y, z, w, t, f, r0, r1, r2, r3, r4, r5, r6
    init()
    r_poly = poly_pow_mod(0b10, frame % (2 ** 128 - 1), 0x100000201a8362f671442057eea368001)
    s_x = s_y = s_z = s_w = 0
    while r_poly > 0:
        if r_poly & 1:
            s_x ^= x
            s_y ^= y
            s_z ^= z
            s_w ^= w
        r_poly >>= 1
        ascend()
    x, y, z, w = s_x, s_y, s_z, s_w
    f = frame
    for _ in range(7):
        roll()


def slot(fill, num1):
    if num1 >= slotvalue[fill - 1][2]:
        return 3
    elif num1 >= slotvalue[fill - 1][1]:
        return 2
    elif num1 >= slotvalue[fill - 1][0]:
        return 1
    else:
        return 0


def rare(sl, fill):
    num1 = sl * 2 + fill
    if kind == 0:
        return 10 if num1 >= 13 else 9 if num1 >= 8 else 8
    elif kind == 1:
        return 7 if num1 >= 13 else 6 if num1 >= 8 else 5
    elif kind == 2:
        return 4 if num1 >= 8 else 3
    else:
        return 2 if num1 >= 8 else 1


def getcharm(_origin):
    c = [0] * 8
    id1 = r0 % len(skill1)
    id2 = r3 % len(skill2)
    s1 = sp1[id1][1]
    s2 = sp2[id2][1]
    c[0] = skill1[id1]
    tmp1 = r1 % (sp1[id1][1] - sp1[id1][0] + 1) + sp1[id1][0]
    c[1] = tmp1
    if r2 % 100 >= th:
        c[2] = skill2[id2]
        if _origin == 1 and r4 % 2 == 0:
            q4, q5 = r5, r6
            tmp2 = q4 % (sp2[id2][0] + 1) - sp2[id2][0]
        else:
            if _origin == 1:
                q4, q5 = r5, r6
            else:
                q4, q5 = r4, r5
            tmp2 = q4 % sp2[id2][1] + 1
        c[3] = tmp2
        if skill1[id1] == skill2[id2] or tmp2 < 0:
            tmp2 = 0
    else:
        c[2] = -1
        tmp2 = 0
        q5 = r3
    tmp0 = (tmp1 * s2 + tmp2 * s1) * 10 // (s1 * s2)
    c[4] = slot(tmp0, q5 % 100)
    c[5] = tmp0
    c[6] = q5 % 100
    c[7] = rare(c[4], c[5])
    return c


def watch_str(fr):
    a = [0] * 5
    a[0] = fr // 2592000
    a[1] = (fr % 2592000) // 108000
    a[2] = (fr % 108000) // 1800
    a[3] = (fr % 1800) // 30
    a[4] = fr % 30
    return '{0}d {1}h {2}m {3}s {4}f'.format(*a)


def charm_to_dict(c):
    sk1_name = skill[c[0]].strip() if c[0] < len(skill) else str(c[0])
    sk2_name = skill[c[2]].strip() if c[2] != -1 and c[2] < len(skill) else None
    return {
        'skill1': sk1_name,
        'sp1': c[1],
        'skill2': sk2_name,
        'sp2': c[3] if c[2] != -1 else None,
        'slots': c[4],
        'fill': c[5],
        'rand': c[6],
        'rare': c[7],
    }


def parameter(str1, num1, str2, num2, num3, str3):
    _id1 = skill1.index(skill.index(str1)) if str1 != '' else -1
    _sp1 = num1
    _id2 = skill2.index(skill.index(str2)) if str2 != '' else -1
    _sp2 = num2
    if _id1 == -1 and _id2 == -1:
        _id1 = 0
    _slot = num3
    _origin = origin.index(str3)
    _len1 = len(skill1)
    _len2 = len(skill2)
    return [_id1, _sp1, _id2, _sp2, _slot, _origin, _len1, _len2]


def search(start, step, p, limit=200):
    _id1, _sp1, _id2, _sp2, _slot, _origin, _len1, _len2 = p
    jump(start)
    skip2 = (_id2 == -1)
    results = []
    for _ in range(step):
        roll()
        if r0 % _len1 == _id1 and (skip2 or r2 % 100 >= th and r3 % _len2 == _id2):
            c = getcharm(_origin)
            if c[1] == _sp1 and c[4] == _slot:
                cond = (c[3] == _sp2) if not skip2 else (c[2] == -1 or c[2] == c[0] or c[3] == 0)
                if cond:
                    frame = f - 7
                    results.append({'frame': frame, 'time': watch_str(frame), 'charm': charm_to_dict(c)})
                    if len(results) >= limit:
                        break
    return results


def search_greater(start, step, p, limit=200):
    _id1, _sp1, _id2, _sp2, _slot, _origin, _len1, _len2 = p
    jump(start)
    skip1 = (_id1 == -1)
    skip2 = (_id2 == -1)
    results = []
    for _ in range(step):
        roll()
        if (skip1 or r0 % _len1 == _id1) and (skip2 or r2 % 100 >= th and r3 % _len2 == _id2):
            c = getcharm(_origin)
            if skip1 and c[0] == c[2]:
                continue
            if (skip1 or c[1] >= _sp1) and (skip2 or c[3] >= _sp2) and c[4] >= _slot:
                frame = f - 7
                results.append({'frame': frame, 'time': watch_str(frame), 'charm': charm_to_dict(c)})
                if len(results) >= limit:
                    break
    return results


def search_any_skill2(start, step, p, limit=200):
    """skill2 は何でもよいが必ず存在し sp2 >= 指定値、skill1 と slots は通常通り絞り込む。"""
    _id1, _sp1, _id2, _sp2, _slot, _origin, _len1, _len2 = p
    jump(start)
    skip1 = (_id1 == -1)
    results = []
    for _ in range(step):
        roll()
        if skip1 or r0 % _len1 == _id1:
            c = getcharm(_origin)
            if skip1 and c[0] == c[2]:
                continue
            if (skip1 or c[1] >= _sp1) and c[2] != -1 and c[3] >= _sp2 and c[4] >= _slot:
                frame = f - 7
                results.append({'frame': frame, 'time': watch_str(frame), 'charm': charm_to_dict(c)})
                if len(results) >= limit:
                    break
    return results


def get_skill_list(pool):
    """Return list of skill names for the current color (skill1 or skill2)."""
    idx_list = skill1 if pool == 1 else skill2
    return [skill[i].strip() for i in idx_list]


def get_origin_list():
    return list(origin)


def get_kinds_list():
    return list(kinds)
