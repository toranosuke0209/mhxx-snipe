"""
事前計算済みnumpyキャッシュからお守りを検索するモジュール。
charm_cache.npy が存在しない場合は None を返す（フォールバック用）。
"""

import os
import numpy as np
import core

CACHE_PATH = os.path.join(os.path.dirname(__file__), 'charm_cache.npy')
DTYPE = np.dtype([
    ('s1', np.uint8),
    ('p1', np.uint8),
    ('s2', np.uint8),  # 255 = なし
    ('p2', np.int8),
    ('sl', np.uint8),
    ('ra', np.uint8),
])

_cache = None
_cache_size = 0


def load():
    global _cache, _cache_size
    if not os.path.exists(CACHE_PATH):
        return False
    _cache = np.lib.format.open_memmap(CACHE_PATH, mode='r', dtype=DTYPE)
    _cache_size = len(_cache)
    return True


def is_ready():
    return _cache is not None and _cache_size > 0


def cache_size():
    return _cache_size


def search(start, step, p, limit=200):
    """キャッシュから検索。Noneを返した場合はcore.searchにフォールバック。"""
    if not is_ready():
        return None
    _id1, _sp1, _id2, _sp2, _slot, _origin, _len1, _len2 = p
    end = min(start + step, _cache_size)
    if start >= _cache_size:
        return None  # キャッシュ範囲外

    arr = _cache[start:end]
    frames = np.arange(start, end)

    # _id1/_id2 はskill1/skill2リストのインデックス → global skill indexに変換
    gs1 = core.skill1[_id1] if _id1 >= 0 else -1
    gs2 = core.skill2[_id2] if _id2 >= 0 else -1

    # skill1フィルタ
    if gs1 >= 0:
        mask = (arr['s1'] == gs1) & (arr['p1'] >= _sp1) & (arr['sl'] >= _slot)
    else:
        mask = arr['sl'] >= _slot

    # skill2フィルタ
    if gs2 >= 0:
        mask &= (arr['s2'] == gs2) & (arr['p2'] >= _sp2)

    hit_frames = frames[mask]
    if len(hit_frames) == 0:
        return []

    # 結果を辞書に変換
    results = []
    for fr in hit_frames[:limit]:
        c = _cache[fr]
        s2_id = int(c['s2']) if c['s2'] != 255 else -1
        charm = {
            'skill1': core.skill[int(c['s1'])].strip(),
            'sp1': int(c['p1']),
            'skill2': core.skill[s2_id].strip() if s2_id != -1 else None,
            'sp2': int(c['p2']) if s2_id != -1 else None,
            'slots': int(c['sl']),
            'rare': int(c['ra']),
        }
        results.append({'frame': int(fr), 'time': core.watch_str(int(fr)), 'charm': charm})
    return results


def search_greater(start, step, p, limit=200):
    """以上検索（skill1もany可）。"""
    if not is_ready():
        return None
    _id1, _sp1, _id2, _sp2, _slot, _origin, _len1, _len2 = p
    end = min(start + step, _cache_size)
    if start >= _cache_size:
        return None

    arr = _cache[start:end]
    frames = np.arange(start, end)

    skip1 = (_id1 == -1)
    skip2 = (_id2 == -1)
    gs1 = core.skill1[_id1] if not skip1 else -1
    gs2 = core.skill2[_id2] if not skip2 else -1

    if skip1:
        mask = (arr['p1'] >= _sp1) & (arr['sl'] >= _slot)
        # skill1==skill2 除外
        mask &= (arr['s1'] != arr['s2'])
    else:
        mask = (arr['s1'] == gs1) & (arr['p1'] >= _sp1) & (arr['sl'] >= _slot)

    if not skip2:
        mask &= (arr['s2'] == gs2) & (arr['p2'] >= _sp2)

    hit_frames = frames[mask]
    if len(hit_frames) == 0:
        return []

    results = []
    for fr in hit_frames[:limit]:
        c = _cache[fr]
        s2_id = int(c['s2']) if c['s2'] != 255 else -1
        charm = {
            'skill1': core.skill[int(c['s1'])].strip(),
            'sp1': int(c['p1']),
            'skill2': core.skill[s2_id].strip() if s2_id != -1 else None,
            'sp2': int(c['p2']) if s2_id != -1 else None,
            'slots': int(c['sl']),
            'rare': int(c['ra']),
        }
        results.append({'frame': int(fr), 'time': core.watch_str(int(fr)), 'charm': charm})
    return results


# モジュールロード時にキャッシュを読み込む
load()
