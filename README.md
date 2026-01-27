# 毎日の記録ツール

Pythonとtkinterを使った、テキストと画像を保存できる毎日の記録管理ツールです。

## 機能

- **記録管理**: 日付ごとにテキストと画像を記録
- **カレンダービュー**: 月別カレンダーで記録を視覚的に確認
- **画像添付**: 複数の画像を添付可能（自動サムネイル生成）
- **タグと気分**: タグ付けと気分（良い/普通/悪い）の記録
- **Markdownエクスポート**: 記録をMarkdown形式でエクスポート

## インストール

### 必要要件

- Python 3.8以上

### セットアップ

1. 依存パッケージをインストール:

```bash
pip install -r requirements.txt
```

## 使い方

### 起動

```bash
python main.py
```

### 基本操作

1. **記録の作成・編集**
   - カレンダーで日付を選択
   - 「記録を追加/編集」ボタンをクリック
   - テキストを入力、タグ・気分を設定
   - 「保存」ボタンで保存

2. **画像の追加**
   - 記録編集画面で「画像を追加」ボタンをクリック
   - 画像ファイル（JPG, PNG, GIF, BMP）を選択
   - サムネイルが自動生成されます

3. **記録の閲覧**
   - カレンダーで日付を選択すると、右側にプレビュー表示
   - サムネイルをクリックで拡大表示

4. **Markdownエクスポート**
   - 記録を選択
   - 「Markdownエクスポート」ボタンをクリック
   - `exports/` ディレクトリに保存されます

### カレンダーの操作

- **< / >**: 前月/次月へ移動
- **今日**: 今日の日付へジャンプ
- **緑色の日**: 記録が存在する日
- **青色の背景**: 今日の日付
- **青色の強調**: 選択中の日付

## データ保存

- **記録データ**: `data/records.json`
- **画像ファイル**: `data/images/YYYY/MM/` （年月ごとに分類）
- **エクスポート**: `exports/`

## プロジェクト構成

```
継続記録ツール/
├── main.py                     # エントリーポイント
├── requirements.txt            # 依存パッケージ
├── src/
│   ├── app.py                 # アプリケーションメインクラス
│   ├── models/
│   │   ├── record.py          # Record/ImageAttachmentクラス
│   │   └── storage.py         # JSON読み書き
│   ├── views/
│   │   ├── main_window.py     # メインウィンドウ
│   │   ├── calendar_view.py   # カレンダー表示
│   │   ├── record_editor.py   # 記録入力・編集
│   │   └── record_viewer.py   # 記録閲覧
│   ├── controllers/
│   │   ├── record_controller.py    # CRUD操作
│   │   └── export_controller.py    # エクスポート機能
│   └── utils/
│       ├── image_handler.py        # 画像処理
│       └── markdown_exporter.py    # Markdown変換
├── data/
│   ├── records.json           # 記録データ
│   └── images/YYYY/MM/        # 画像ファイル
└── exports/                   # エクスポート先
```

## 技術スタック

- **Python 3.8+**
- **tkinter**: GUI（標準ライブラリ）
- **Pillow**: 画像処理
- **JSON**: データ保存

## ライセンス

MIT License
