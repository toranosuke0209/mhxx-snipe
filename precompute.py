"""
デフォルトシードのお守りデータを事前計算してnumpyバイナリファイルに保存する。
100Mフレーム × 6バイト = 約600MB

実行: python3 precompute.py [max_frames]
"""

import os
import sys
import time
import numpy as np
import core

CACHE_PATH = os.path.join(os.path.dirname(__file__), 'charm_cache.npy')
DTYPE = np.dtype([
    ('s1', np.uint8),   # skill1_id
    ('p1', np.uint8),   # sp1 (1-20)
    ('s2', np.uint8),   # skill2_id (255 = なし)
    ('p2', np.int8),    # sp2 (-20 to 20)
    ('sl', np.uint8),   # slots (0-3)
    ('ra', np.uint8),   # rare (5-10)
])

DEFAULT_MAX = 100_000_000
BATCH = 1_000_000


def build_cache(max_frames=DEFAULT_MAX, origin=0):
    core.set_seed(core.DEFAULT_SEED)
    core.set_blue()
    core.set_ja()

    print(f"キャッシュ生成開始: {max_frames:,} フレーム → {CACHE_PATH}")
    arr = np.lib.format.open_memmap(CACHE_PATH, mode='w+', dtype=DTYPE, shape=(max_frames,))

    t0 = time.time()
    for batch_start in range(0, max_frames, BATCH):
        count = min(BATCH, max_frames - batch_start)
        # generate_range(N, count) の結果[i] = フレーム N+i+1 のデータ
        data = core.generate_range(batch_start, count, origin)
        for i, (s1, p1, s2, p2, sl, ra) in enumerate(data):
            idx = batch_start + i + 1  # 実際のフレーム番号
            if idx >= max_frames:
                break
            arr[idx]['s1'] = s1 & 0xFF
            arr[idx]['p1'] = p1 & 0xFF
            arr[idx]['s2'] = s2 & 0xFF if s2 != -1 else 255
            arr[idx]['p2'] = p2
            arr[idx]['sl'] = sl
            arr[idx]['ra'] = ra
        arr.flush()
        elapsed = time.time() - t0
        done = batch_start + count
        rate = done / elapsed
        eta = (max_frames - done) / rate if rate > 0 else 0
        print(f"  {done:>12,} / {max_frames:,}  ({done/max_frames*100:.1f}%)  "
              f"{elapsed:.0f}s経過  残り約{eta:.0f}s", flush=True)

    print(f"完了: {time.time()-t0:.1f}s  ファイルサイズ: {os.path.getsize(CACHE_PATH)/1e6:.0f}MB")


if __name__ == '__main__':
    max_frames = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MAX
    build_cache(max_frames)
