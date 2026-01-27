"""記録閲覧ビュー"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import os


class RecordViewer:
    """記録の表示（プレビュー）"""

    def __init__(self, parent, record_controller):
        self.parent = parent
        self.record_controller = record_controller
        self.current_date = None
        self.thumbnail_refs = []  # ImageTkのガベージコレクション防止

        self._create_widgets()
        self._layout_widgets()

    def _create_widgets(self):
        """ウィジェットを作成"""
        # スクロール可能なメインフレーム
        self.canvas = tk.Canvas(self.parent)
        self.scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.content_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.content_frame, anchor=tk.NW)

        # 記録なしメッセージ
        self.no_record_label = ttk.Label(
            self.content_frame,
            text="この日の記録はありません",
            font=("", 12),
            foreground="gray"
        )

        # 記録情報フレーム
        self.info_frame = ttk.Frame(self.content_frame)

        # 気分表示
        self.mood_label = ttk.Label(self.info_frame, text="", font=("", 10))

        # タグ表示
        self.tags_label = ttk.Label(self.info_frame, text="", font=("", 9), foreground="blue")

        # 更新日時表示
        self.updated_label = ttk.Label(self.info_frame, text="", font=("", 8), foreground="gray")

        # テキスト表示エリア
        self.text_frame = ttk.LabelFrame(self.content_frame, text="記録テキスト", padding=10)
        self.text_area = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            height=10,
            font=("", 10),
            state=tk.DISABLED,
            bg="#f5f5f5"
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # 画像表示エリア
        self.image_frame = ttk.LabelFrame(self.content_frame, text="添付画像", padding=10)
        self.image_container = ttk.Frame(self.image_frame)

        # スクロール領域を更新
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def _layout_widgets(self):
        """ウィジェットをレイアウト"""
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def display_record(self, date: str):
        """指定日の記録を表示"""
        self.current_date = date
        self.thumbnail_refs.clear()

        # 既存のウィジェットを非表示
        self.no_record_label.pack_forget()
        self.info_frame.pack_forget()
        self.text_frame.pack_forget()
        self.image_frame.pack_forget()

        # 記録を取得
        record = self.record_controller.get_record(date)

        if not record:
            # 記録なし
            self.no_record_label.pack(pady=50)
            return

        # 記録あり
        # 情報表示
        self.info_frame.pack(fill=tk.X, pady=(0, 10))

        # 気分
        mood_text = ""
        if record.mood == "good":
            mood_text = "気分: 😊 良い"
        elif record.mood == "neutral":
            mood_text = "気分: 😐 普通"
        elif record.mood == "bad":
            mood_text = "気分: 😞 悪い"

        self.mood_label.config(text=mood_text)
        if mood_text:
            self.mood_label.pack(anchor=tk.W, pady=(0, 5))
        else:
            self.mood_label.pack_forget()

        # タグ
        if record.tags:
            tags_text = "タグ: " + ", ".join(record.tags)
            self.tags_label.config(text=tags_text)
            self.tags_label.pack(anchor=tk.W, pady=(0, 5))
        else:
            self.tags_label.pack_forget()

        # 更新日時
        updated_text = f"最終更新: {record.updated_at}"
        self.updated_label.config(text=updated_text)
        self.updated_label.pack(anchor=tk.W)

        # テキスト表示
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", record.text if record.text else "(テキストなし)")
        self.text_area.config(state=tk.DISABLED)

        # 画像表示
        if record.images:
            self.image_frame.pack(fill=tk.BOTH, pady=(0, 10))

            # 既存の画像をクリア
            for widget in self.image_container.winfo_children():
                widget.destroy()

            # 画像を並べて表示
            for idx, image in enumerate(record.images):
                img_frame = ttk.Frame(self.image_container, relief=tk.RAISED, borderwidth=1)
                img_frame.pack(side=tk.LEFT, padx=5, pady=5)

                # サムネイル表示
                try:
                    if os.path.exists(image.thumbnail_path):
                        img = Image.open(image.thumbnail_path)
                        img.thumbnail((120, 120))
                        photo = ImageTk.PhotoImage(img)
                        self.thumbnail_refs.append(photo)

                        img_label = ttk.Label(img_frame, image=photo, cursor="hand2")
                        img_label.pack()

                        # クリックで拡大表示
                        img_label.bind("<Button-1>", lambda e, path=image.path: self._show_full_image(path))
                    else:
                        ttk.Label(img_frame, text="画像なし").pack()
                except Exception as e:
                    ttk.Label(img_frame, text="読込エラー").pack()

                # キャプション
                if image.caption:
                    ttk.Label(
                        img_frame,
                        text=image.caption[:30] + "..." if len(image.caption) > 30 else image.caption,
                        font=("", 8)
                    ).pack(pady=(2, 0))

            self.image_container.pack()

        # スクロール領域を更新
        self.content_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _show_full_image(self, image_path: str):
        """画像を拡大表示"""
        if not os.path.exists(image_path):
            return

        # 新しいウィンドウで画像を表示
        window = tk.Toplevel(self.parent)
        window.title("画像表示")

        try:
            img = Image.open(image_path)

            # 画面サイズに合わせてリサイズ
            max_width = 800
            max_height = 600
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(img)

            label = ttk.Label(window, image=photo)
            label.image = photo  # 参照を保持
            label.pack()

        except Exception as e:
            ttk.Label(window, text=f"画像を読み込めません: {e}").pack(padx=20, pady=20)
