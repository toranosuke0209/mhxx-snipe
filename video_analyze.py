"""
動画から調合所持数の変化を自動抽出するモジュール。
Switch MHXX (1080p) のキャプチャ動画を想定。

OCR部分は digit_templates/ にテンプレート画像が揃ったら実装する（TODO）。
"""

import base64
import io
import os
import tempfile

import cv2
import numpy as np


# ── テンプレートマッチング（TODO: スクショが揃ったら実装） ──────────────
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'digit_templates')

def _load_templates():
    """0〜9のテンプレート画像をロードして返す。未実装時は None。"""
    templates = {}
    if not os.path.isdir(TEMPLATES_DIR):
        return None
    for d in range(10):
        path = os.path.join(TEMPLATES_DIR, f'{d}.png')
        if not os.path.exists(path):
            return None
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
        templates[d] = img
    return templates

_TEMPLATES = None  # 起動時に一度だけロード


def _read_digit(roi_gray, templates):
    """1桁のROI画像をテンプレートマッチングで読む。失敗時は -1。"""
    best_val, best_digit = -1, -1
    for digit, tmpl in templates.items():
        if roi_gray.shape[0] < tmpl.shape[0] or roi_gray.shape[1] < tmpl.shape[1]:
            continue
        res = cv2.matchTemplate(roi_gray, tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > best_val:
            best_val, best_digit = max_val, digit
    return best_digit if best_val > 0.7 else -1


def _read_two_digit(roi_gray, templates):
    """2桁の所持数を左右に分割して読む。失敗時は -1。"""
    h, w = roi_gray.shape
    mid = w // 2
    tens = _read_digit(roi_gray[:, :mid], templates)
    ones = _read_digit(roi_gray[:, mid:], templates)
    if tens < 0 or ones < 0:
        return -1
    return tens * 10 + ones


# ── 動画処理ユーティリティ ──────────────────────────────────────────────

def _save_upload_to_tmp(file_storage):
    """FlaskのFileStorageを一時ファイルに保存してパスを返す。"""
    suffix = os.path.splitext(file_storage.filename or '.mp4')[1] or '.mp4'
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    file_storage.save(tmp.name)
    tmp.close()
    return tmp.name


# ── 公開API ────────────────────────────────────────────────────────────

def extract_first_frame(file_storage):
    """
    動画の最初のフレームをBase64エンコードJPEGで返す。
    フロントエンドで所持数の領域を選択させるために使う。
    """
    tmp_path = _save_upload_to_tmp(file_storage)
    try:
        cap = cv2.VideoCapture(tmp_path)
        ok, frame = cap.read()
        cap.release()
        if not ok:
            raise ValueError('動画の読み込みに失敗しました')
        _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        b64 = base64.b64encode(buf.tobytes()).decode('ascii')
        h, w = frame.shape[:2]
        return {'image': f'data:image/jpeg;base64,{b64}', 'width': w, 'height': h}
    finally:
        os.unlink(tmp_path)


def extract_counts(file_storage, x, y, width, height):
    """
    動画全体を走査し、指定領域の所持数が変化したフレームの値を返す。

    Returns:
        {'counts': [0, 3, 6, 9, ...], 'combo_str': '00 03 06 09 ...'}
        or {'error': '...', 'todo': True} if templates are not ready
    """
    global _TEMPLATES
    if _TEMPLATES is None:
        _TEMPLATES = _load_templates()

    if _TEMPLATES is None:
        # テンプレート未実装 — スクリーンショットが揃ったら digit_templates/ に追加する
        return {
            'error': 'digit_templates/ にテンプレート画像がありません。スクリーンショットから作成してください。',
            'todo': True,
        }

    tmp_path = _save_upload_to_tmp(file_storage)
    try:
        cap = cv2.VideoCapture(tmp_path)
        counts = []
        prev_val = -1

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            roi = frame[y:y+height, x:x+width]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            val = _read_two_digit(gray, _TEMPLATES)

            if val >= 0 and val != prev_val:
                counts.append(val)
                prev_val = val

        cap.release()

        if len(counts) < 2:
            return {'error': '所持数の変化を検出できませんでした。領域を確認してください。'}

        combo_str = ' '.join(f'{v:02d}' for v in counts)
        return {'counts': counts, 'combo_str': combo_str}
    finally:
        os.unlink(tmp_path)
