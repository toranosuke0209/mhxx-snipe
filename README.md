# MHXX お守りスナイプ ローカル版

[mhxx-rng](https://github.com/apmnnn/mhxx-rng) をベースに作成したローカル Web アプリです。  
Google Colab なしで、ブラウザだけでお守りの乱数検索ができます。

## 起動方法

```bash
pip install -r requirements.txt
python app.py
```

ブラウザで http://localhost:5000 を開いてください。

## 機能

- お守りカラー選択（風化/古び/光る/なぞ）
- スキル・ポイント・スロット指定での完全一致 / 以上検索
- シード値の変更
- 日本語 / 英語対応

## 注意事項

- 乱数の計算は元の [apmnnn/mhxx-rng](https://github.com/apmnnn/mhxx-rng) の実装に従っています
- Numba による高速化は未使用（純粋な Python のため大きな検索範囲は時間がかかります）
