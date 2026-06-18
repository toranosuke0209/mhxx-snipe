"""
動画から調合所持数の変化を自動抽出するモジュール。
Tesseract OCRを使用。領域指定は任意（未指定時はデフォルト比率を使用）。
"""

import base64
import io
import os
import re
import tempfile

import cv2
import numpy as np
from PIL import Image, ImageEnhance

try:
    import pytesseract
    _TESSERACT_OK = True
except ImportError:
    _TESSERACT_OK = False

# デフォルト領域比率（非ズーム 1280x720 で検証済み）
DEFAULT_X_RATIO = 0.55
DEFAULT_Y_RATIO = 0.33
DEFAULT_W_RATIO = 0.13
DEFAULT_H_RATIO = 0.09


def _save_upload_to_tmp(file_storage):
    suffix = os.path.splitext(file_storage.filename or '.mp4')[1] or '.mp4'
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    file_storage.save(tmp.name)
    tmp.close()
    return tmp.name


def _ocr_count(frame_bgr, x, y, w, h):
    """指定領域からX/99形式の数値を読み取る。失敗時はNone。"""
    roi = frame_bgr[y:y+h, x:x+w]
    pil = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
    pil = pil.resize((pil.width * 6, pil.height * 6), Image.LANCZOS)
    gray = pil.convert('L')
    bw = gray.point(lambda v: 255 if v > 150 else 0)
    raw = pytesseract.image_to_string(bw, config='--psm 6 -c tessedit_char_whitelist=0123456789/')
    m = re.search(r'(\d+)/\d+', raw)
    if m:
        return int(m.group(1))
    return None


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
        # デフォルト領域をピクセル値で返す
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
    if not _TESSERACT_OK:
        return {'error': 'pytesseract がインストールされていません。'}

    tmp_path = _save_upload_to_tmp(file_storage)
    try:
        cap = cv2.VideoCapture(tmp_path)
        fw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        fh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 領域未指定ならデフォルト比率で計算
        if width == 0 or height == 0:
            x = int(fw * DEFAULT_X_RATIO)
            y = int(fh * DEFAULT_Y_RATIO)
            width  = int(fw * DEFAULT_W_RATIO)
            height = int(fh * DEFAULT_H_RATIO)

        counts = []
        prev_val = None
        frame_idx = 0
        fps = cap.get(cv2.CAP_PROP_FPS) or 30

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            # 毎フレームは重いので1秒に数回サンプリング（約6fps）
            if frame_idx % max(1, int(fps / 6)) == 0:
                val = _ocr_count(frame, x, y, width, height)
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
