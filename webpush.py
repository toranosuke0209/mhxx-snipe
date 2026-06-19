"""
Web Push通知モジュール。
VAPIDキーを使いサーバーからブラウザにプッシュ通知を送信する。
"""

import json
import threading
import time

from pywebpush import webpush, WebPushException

VAPID_PRIVATE_KEY = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIK005Q0s7Aolzp9n0BcPwJDj/z/aFOBfBszjMYO8J8qXoAoGCCqGSM49
AwEHoUQDQgAEdxGC+uZg2dd9EYoI6//oSfybz/Hqi9b5WzF1DMb4oPVE0KPTcSTF
ihnlg4xmBL3caRuLuzMaPxFi8bOlDqdsHQ==
-----END EC PRIVATE KEY-----"""

VAPID_PUBLIC_KEY = "BHcRgvrmYNnXfRGKCOv_6En8m8_x6ovW-VsxdQzG-KD1RNCj03EkxYoZ5YOMZgS93Gkbi7szGj8RYvGzpQ6nbB0"

VAPID_CLAIMS = {"sub": "mailto:tots.ai@ezweb.ne.jp"}

# username -> {"subscription": {...}, "timer": Thread}
_scheduled: dict = {}
_lock = threading.Lock()


def send_push(subscription_info: dict, title: str, body: str):
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps({"title": title, "body": body}),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS,
        )
    except WebPushException as e:
        print(f"[webpush] error: {e}")


def schedule_notification(username: str, subscription: dict, delay_sec: float, title: str, body: str):
    """delay_sec 秒後にプッシュ通知を送る。同ユーザーの既存タイマーはキャンセル。"""
    cancel_notification(username)

    def _run():
        time.sleep(delay_sec)
        with _lock:
            if _scheduled.get(username, {}).get("active"):
                send_push(subscription, title, body)
                _scheduled.pop(username, None)

    t = threading.Thread(target=_run, daemon=True)
    with _lock:
        _scheduled[username] = {"active": True, "thread": t}
    t.start()


def cancel_notification(username: str):
    with _lock:
        entry = _scheduled.pop(username, None)
        if entry:
            entry["active"] = False
