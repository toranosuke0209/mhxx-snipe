from flask import Flask, render_template, request, jsonify
import core
import video_analyze
import charm_cache
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), 'favs.db')


def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute('''CREATE TABLE IF NOT EXISTS favs (
        key TEXT PRIMARY KEY,
        result_json TEXT NOT NULL,
        username TEXT NOT NULL DEFAULT 'admin',
        memo TEXT NOT NULL DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    for col, definition in [("username", "TEXT NOT NULL DEFAULT 'admin'"), ("memo", "TEXT NOT NULL DEFAULT ''")]:
        try:
            con.execute(f"ALTER TABLE favs ADD COLUMN {col} {definition}")
        except Exception:
            pass
    con.execute('''CREATE TABLE IF NOT EXISTS offset_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        target_frame INTEGER NOT NULL,
        actual_frame INTEGER NOT NULL,
        diff INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS search_presets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        name TEXT NOT NULL,
        conditions_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    con.commit()
    return con

COLOR_SETTERS = {
    'blue': core.set_blue,
    'red': core.set_red,
    'yellow': core.set_yellow,
    'white': core.set_white,
}

LANG_SETTERS = {
    'ja': core.set_ja,
    'en': core.set_en,
}


def apply_config(lang, color):
    LANG_SETTERS.get(lang, core.set_ja)()
    COLOR_SETTERS.get(color, core.set_blue)()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/skills')
def get_skills():
    lang = request.args.get('lang', 'ja')
    color = request.args.get('color', 'blue')
    apply_config(lang, color)
    skill1_names = core.get_skill_list(1)
    skill2_names = core.get_skill_list(2)
    skill1_max = [sp[1] for sp in core.sp1]
    skill2_max = [sp[1] for sp in core.sp2]
    return jsonify({
        'skill1': skill1_names,
        'skill1_max': skill1_max,
        'skill2': skill2_names,
        'skill2_max': skill2_max,
        'origin': core.get_origin_list(),
        'kinds': core.get_kinds_list(),
    })


@app.route('/api/search', methods=['POST'])
def do_search():
    data = request.json
    lang = data.get('lang', 'ja')
    color = data.get('color', 'blue')
    mode = data.get('mode', 'exact')

    seed_raw = data.get('seed', '')
    if seed_raw:
        try:
            parts = [int(x.strip(), 16) for x in seed_raw.split(',')]
            if len(parts) == 4:
                core.set_seed(parts)
            else:
                return jsonify({'error': 'Seed must be 4 hex values separated by commas'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid seed format'}), 400
    else:
        core.set_seed(core.DEFAULT_SEED)

    apply_config(lang, color)

    start = int(data.get('start', 0))
    origin_name = data.get('origin', core.origin[0])
    # キャッシュ使用時は上限なし、未使用時は10Mまで
    use_cache = not seed_raw and charm_cache.is_ready() and origin_name == core.origin[0]
    step = int(data.get('step', 100000)) if use_cache else min(int(data.get('step', 100000)), 10000000)
    skill1_name = data.get('skill1', '')
    sp1 = int(data.get('sp1', 0))
    skill2_name = data.get('skill2', '')
    sp2 = int(data.get('sp2', 0))
    slots = int(data.get('slots', 0))

    try:
        _origin = core.origin.index(origin_name)
    except ValueError:
        _origin = 0

    def find_skill1_id(name):
        if not name:
            return -1
        try:
            skill_idx = core.skill.index(name) if name in core.skill else next(
                (i for i, s in enumerate(core.skill) if s.strip() == name), -1)
            return core.skill1.index(skill_idx)
        except (ValueError, StopIteration):
            return -1

    def find_skill2_id(name):
        if not name:
            return -1
        try:
            skill_idx = core.skill.index(name) if name in core.skill else next(
                (i for i, s in enumerate(core.skill) if s.strip() == name), -1)
            return core.skill2.index(skill_idx)
        except (ValueError, StopIteration):
            return -1

    skill1_any = (skill1_name == '__any__')
    skill2_any = (skill2_name == '__any__')
    _id1 = -1 if (skill1_any or not skill1_name) else find_skill1_id(skill1_name)
    _id2 = -1 if (skill2_any or not skill2_name) else find_skill2_id(skill2_name)

    if _id1 == -1 and _id2 == -1 and not skill1_any and not skill2_any:
        _id1 = 0

    p = [_id1, sp1, _id2, sp2, slots, _origin, len(core.skill1), len(core.skill2)]

    try:
        results = None
        used_cache = False
        # デフォルトシード使用時はキャッシュを優先
        if not seed_raw and charm_cache.is_ready() and not skill2_any:
            if mode == 'exact':
                results = charm_cache.search(start, step, p)
            else:
                results = charm_cache.search_greater(start, step, p)
            if results is not None:
                used_cache = True

        if results is None:
            if skill2_any:
                results = core.search_any_skill2(start, step, p)
            elif mode == 'exact':
                results = core.search(start, step, p)
            else:
                results = core.search_greater(start, step, p)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'results': results, 'count': len(results), 'cached': used_cache})


@app.route('/api/search_combo', methods=['POST'])
def do_search_combo():
    data = request.json
    seed_raw = data.get('seed', '')
    if seed_raw:
        try:
            parts = [int(x.strip(), 16) for x in seed_raw.split(',')]
            if len(parts) == 4:
                core.set_seed(parts)
            else:
                return jsonify({'error': 'Seed must be 4 hex values separated by commas'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid seed format'}), 400
    else:
        core.set_seed(core.DEFAULT_SEED)

    combo_str = data.get('combo', '').strip()
    start = int(data.get('start', 0))
    step = min(int(data.get('step', 1000000)), 10000000)

    try:
        result = core.search_combo(start, step, combo_str)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route('/api/video_frame', methods=['POST'])
def video_first_frame():
    """動画の最初のフレームをJPEGで返す（領域選択用）"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    f = request.files['video']
    try:
        result = video_analyze.extract_first_frame(f)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(result)


@app.route('/api/video_analyze', methods=['POST'])
def video_analyze_route():
    """動画から所持数の変化を自動抽出する"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    f = request.files['video']
    try:
        x      = int(request.form.get('x', 0))
        y      = int(request.form.get('y', 0))
        width  = int(request.form.get('w', 100))
        height = int(request.form.get('h', 40))
        result = video_analyze.extract_counts(f, x, y, width, height)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(result)


@app.route('/api/favs', methods=['GET'])
def favs_list():
    username = request.args.get('username', '')
    if not username:
        return jsonify({'error': 'username required'}), 400
    con = get_db()
    rows = con.execute('SELECT key, result_json, memo FROM favs WHERE username = ? ORDER BY created_at DESC', (username,)).fetchall()
    con.close()
    return jsonify({'favs': [{'key': r['key'], 'result': __import__('json').loads(r['result_json']), 'memo': r['memo'] or ''} for r in rows]})


@app.route('/api/favs', methods=['POST'])
def favs_upsert():
    import json
    data = request.json
    key = data.get('key')
    result = data.get('result')
    username = data.get('username', 'admin')
    memo = data.get('memo', '')
    if not key or result is None:
        return jsonify({'error': 'key and result required'}), 400
    con = get_db()
    con.execute(
        'INSERT INTO favs (key, result_json, username, memo) VALUES (?, ?, ?, ?) ON CONFLICT(key) DO UPDATE SET result_json=excluded.result_json, username=excluded.username, memo=excluded.memo',
        (key, json.dumps(result), username, memo)
    )
    con.commit()
    con.close()
    return jsonify({'ok': True})


@app.route('/api/favs/<path:key>', methods=['DELETE'])
def favs_delete(key):
    username = request.args.get('username') or (request.json or {}).get('username', 'admin')
    con = get_db()
    con.execute('DELETE FROM favs WHERE key = ? AND username = ?', (key, username))
    con.commit()
    con.close()
    return jsonify({'ok': True})


@app.route('/api/favs', methods=['DELETE'])
def favs_clear():
    username = request.args.get('username') or (request.json or {}).get('username', 'admin')
    con = get_db()
    con.execute('DELETE FROM favs WHERE username = ?', (username,))
    con.commit()
    con.close()
    return jsonify({'ok': True})


@app.route('/api/offset_history', methods=['POST'])
def offset_history_post():
    data = request.json
    username = data.get('username', 'admin')
    target_frame = data.get('target_frame')
    actual_frame = data.get('actual_frame')
    if target_frame is None or actual_frame is None:
        return jsonify({'error': 'target_frame and actual_frame required'}), 400
    diff = int(actual_frame) - int(target_frame)
    con = get_db()
    con.execute(
        'INSERT INTO offset_history (username, target_frame, actual_frame, diff) VALUES (?, ?, ?, ?)',
        (username, int(target_frame), int(actual_frame), diff)
    )
    con.commit()
    con.close()
    return jsonify({'ok': True})


@app.route('/api/offset_history', methods=['GET'])
def offset_history_get():
    username = request.args.get('username', '')
    if not username:
        return jsonify({'error': 'username required'}), 400
    con = get_db()
    rows = con.execute(
        'SELECT target_frame, actual_frame, diff, created_at FROM offset_history WHERE username = ? ORDER BY created_at DESC LIMIT 20',
        (username,)
    ).fetchall()
    records = [{'target_frame': r['target_frame'], 'actual_frame': r['actual_frame'], 'diff': r['diff'], 'created_at': r['created_at']} for r in rows]
    avg_diff = (sum(r['diff'] for r in records) / len(records)) if records else None
    con.close()
    return jsonify({'records': records, 'avg_diff': avg_diff})


@app.route('/api/presets', methods=['GET'])
def presets_list():
    import json
    username = request.args.get('username', '')
    if not username:
        return jsonify({'error': 'username required'}), 400
    con = get_db()
    rows = con.execute(
        'SELECT id, name, conditions_json, created_at FROM search_presets WHERE username = ? ORDER BY created_at DESC',
        (username,)
    ).fetchall()
    con.close()
    return jsonify({'presets': [{'id': r['id'], 'name': r['name'], 'conditions': json.loads(r['conditions_json']), 'created_at': r['created_at']} for r in rows]})


@app.route('/api/presets', methods=['POST'])
def presets_save():
    import json
    data = request.json
    username = data.get('username', '')
    name = data.get('name', '').strip()
    conditions = data.get('conditions')
    if not username or not name or conditions is None:
        return jsonify({'error': 'username, name and conditions required'}), 400
    con = get_db()
    cur = con.execute(
        'INSERT INTO search_presets (username, name, conditions_json) VALUES (?, ?, ?)',
        (username, name, json.dumps(conditions))
    )
    con.commit()
    preset_id = cur.lastrowid
    con.close()
    return jsonify({'ok': True, 'id': preset_id})


@app.route('/api/presets/<int:preset_id>', methods=['DELETE'])
def presets_delete(preset_id):
    username = request.args.get('username') or (request.json or {}).get('username', '')
    con = get_db()
    con.execute('DELETE FROM search_presets WHERE id = ? AND username = ?', (preset_id, username))
    con.commit()
    con.close()
    return jsonify({'ok': True})


@app.route('/api/cache_status')
def cache_status():
    return jsonify({
        'ready': charm_cache.is_ready(),
        'frames': charm_cache.cache_size(),
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
