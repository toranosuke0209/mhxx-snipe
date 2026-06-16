from flask import Flask, render_template, request, jsonify
import core
import video_analyze

app = Flask(__name__)

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
    step = min(int(data.get('step', 100000)), 10000000)
    origin_name = data.get('origin', core.origin[0])
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
        if skill2_any:
            results = core.search_any_skill2(start, step, p)
        elif mode == 'exact':
            results = core.search(start, step, p)
        else:
            results = core.search_greater(start, step, p)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'results': results, 'count': len(results)})


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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
