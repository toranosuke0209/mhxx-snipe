"""
動画から調合所持数の変化を自動抽出するモジュール。
テンプレートマッチングで数字を認識（外部OCR不要）。
"""

import base64
import os
import tempfile

import cv2
import numpy as np

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'digit_templates')

# デフォルト領域比率（3.3Xズーム 2532x1170 で検証済み）
DEFAULT_X_RATIO = 0.55
DEFAULT_Y_RATIO = 0.30
DEFAULT_W_RATIO = 0.30
DEFAULT_H_RATIO = 0.15


def _load_templates():
    templates = {}
    for d in range(10):
        path = os.path.join(TEMPLATES_DIR, f'{d}.png')
        if not os.path.exists(path):
            return None
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
        templates[d] = img
    return templates


_TEMPLATES = None


def _read_count_from_region(bw):
    """二値化済み画像から所持数（スラッシュ前の数値）を読み取る。失敗時はNone。"""
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(bw)
    chars = [
        (stats[i][0], stats[i][1], stats[i][2], stats[i][3], stats[i][4])
        for i in range(1, num_labels)
        if stats[i][4] > 50 and stats[i][3] > 10
    ]
    chars.sort(key=lambda c: c[0])
    top_chars = [c for c in chars if c[1] < bw.shape[0] * 0.6]

    if not top_chars:
        return None

    # スラッシュは平均より幅が小さい → スラッシュ前までが所持数
    avg_w = np.mean([c[2] for c in top_chars])
    slash_idx = next((i for i, c in enumerate(top_chars) if c[2] < avg_w * 0.6), None)
    left_chars = top_chars[:slash_idx] if slash_idx is not None else top_chars[:len(top_chars)//2]

    if not left_chars:
        return None

    result = ''
    for (cx, cy, cw, chh, area) in left_chars:
        char_img = bw[cy:cy+chh, cx:cx+cw]
        char_resized = cv2.resize(char_img, (30, 40))
        best_val, best_d = -1, -1
        for d, tmpl in _TEMPLATES.items():
            res = cv2.matchTemplate(char_resized.astype(np.float32), tmpl.astype(np.float32), cv2.TM_CCOEFF_NORMED)
            val = float(res.max())
            if val > best_val:
                best_val, best_d = val, d
        if best_val > 0.5:
            result += str(best_d)

    return int(result) if result else None


def _ocr_frame(frame_bgr, x, y, w, h):
    roi = frame_bgr[y:y+h, x:x+w]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return _read_count_from_region(bw)


def _save_upload_to_tmp(file_storage):
    suffix = os.path.splitext(file_storage.filename or '.mp4')[1] or '.mp4'
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    file_storage.save(tmp.name)
    tmp.close()
    return tmp.name


def extract_first_frame(file_storage):
    """動画の最初のフレームをBase64エンコードJPEGで返す。"""
    tmp_path = _save_upload_to_tmp(file_storage)
    try:
        cap = cv2.VideoCapture(tmp_path)
        ok, frame = cap.read()
        cap.release()
        if not ok:
            raise ValueError('動画の読み込みに失敗しました')
        _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        b64 = base64.b64encode(buf.tobytes()).decode('ascii')
        fh, fw = frame.shape[:2]
        default_rect = {
            'x': int(fw * DEFAULT_X_RATIO),
            'y': int(fh * DEFAULT_Y_RATIO),
            'w': int(fw * DEFAULT_W_RATIO),
            'h': int(fh * DEFAULT_H_RATIO),
        }
        return {'image': f'data:image/jpeg;base64,{b64}', 'width': fw, 'height': fh, 'default_rect': default_rect}
    finally:
        os.unlink(tmp_path)


def extract_counts(file_storage, x, y, width, height):
    """
    動画全体を走査し、所持数が変化したフレームの値を返す。
    x=0,y=0,width=0,height=0 の場合はデフォルト比率を使用。
    """
    global _TEMPLATES
    if _TEMPLATES is None:
        _TEMPLATES = _load_templates()
    if _TEMPLATES is None:
        return {'error': f'digit_templates/ に数字テンプレートがありません。'}

    tmp_path = _save_upload_to_tmp(file_storage)
    try:
        cap = cv2.VideoCapture(tmp_path)
        fw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        fh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30

        if width == 0 or height == 0:
            x      = int(fw * DEFAULT_X_RATIO)
            y      = int(fh * DEFAULT_Y_RATIO)
            width  = int(fw * DEFAULT_W_RATIO)
            height = int(fh * DEFAULT_H_RATIO)

        counts = []
        prev_val = None
        frame_idx = 0
        sample_interval = 1

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_idx % sample_interval == 0:
                val = _ocr_frame(frame, x, y, width, height)
                if val is not None and val != prev_val:
                    counts.append(val)
                    prev_val = val
            frame_idx += 1

        cap.release()

        if len(counts) < 2:
            return {'error': '所持数の変化を検出できませんでした。領域を確認してください。'}

        combo_str = ' '.join(f'{v:02d}' for v in counts)
        return {'counts': counts, 'combo_str': combo_str}
    finally:
        os.unlink(tmp_path)
