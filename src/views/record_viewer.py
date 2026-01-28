"""記録閲覧ビュー"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import os
from .styles import AppStyles


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
        # メインスクロールエリア設定
        # 背景色をカードに合わせるため、親のスタイルに依存
        self.canvas = tk.Canvas(self.parent, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # コンテンツフレーム
        self.content_frame = ttk.Frame(self.canvas, style="Card.TFrame")
        self.canvas.create_window((0, 0), window=self.content_frame, anchor=tk.NW, width=self.parent.winfo_width())

        # ウィンドウサイズ変更時にcanvas windowの幅も更新するためのバインドは別途必要かも
        # 簡易的には、canvasそのものにbindする

        # 記録なしメッセージ
        self.no_record_frame = ttk.Frame(self.content_frame, style="Card.TFrame")
        self.no_record_label = ttk.Label(
            self.no_record_frame,
            text="記録はありません\n「編集する」ボタンから今日の記録を追加しましょう",
            font=("Yu Gothic UI", 12),
            foreground="#9E9E9E",
            justify=tk.CENTER,
            style="Card.TLabel"
        )
        self.no_record_label.pack(pady=50)

        # --- 記録表示用コンテナ ---
        self.record_container = ttk.Frame(self.content_frame, style="Card.TFrame")

        # 気分と更新日時ヘッダー
        self.meta_header_frame = ttk.Frame(self.record_container, style="Card.TFrame")
        
        self.mood_label = ttk.Label(
            self.meta_header_frame, 
            text="", 
            font=("Segoe UI Emoji", 24), # 絵文字用フォント
            style="Card.TLabel"
        )
        
        self.updated_label = ttk.Label(
            self.meta_header_frame, 
            text="", 
            font=("Yu Gothic UI", 9), 
            foreground="#9E9E9E",
            style="Card.TLabel"
        )

        # タグエリア
        self.tags_frame = ttk.Frame(self.record_container, style="Card.TFrame")

        # テキスト表示エリア
        self.text_frame = ttk.Frame(self.record_container, style="Card.TFrame")
        
        # 読み取り専用テキスト（枠線をなくして紙のように見せる）
        self.text_area = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=("Yu Gothic UI", 11),
            state=tk.DISABLED,
            bg="white",
            fg="#333333",
            relief="flat",
            highlightthickness=0,
            pady=10
        )

        # 画像表示エリア
        self.image_frame = ttk.Frame(self.record_container, style="Card.TFrame")
        self.image_header = ttk.Label(
            self.image_frame, 
            text="添付画像", 
            font=("Yu Gothic UI", 10, "bold"),
            foreground="#757575",
            style="Card.TLabel"
        )
        self.image_container = ttk.Frame(self.image_frame, style="Card.TFrame")

        # Canvasのリサイズイベント
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_canvas_configure(self, event):
        """Canvasの幅に合わせて内部フレームの幅を調整"""
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)

    def _layout_widgets(self):
        """ウィジェットをレイアウト"""
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def display_record(self, date: str):
        """指定日の記録を表示"""
        self.current_date = date
        self.thumbnail_refs.clear()

        # 表示リセット
        self.no_record_frame.pack_forget()
        self.record_container.pack_forget()
        
        # 記録を取得
        record = self.record_controller.get_record(date)

        if not record:
            self.no_record_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            return

        # --- 記録あり ---
        self.record_container.pack(fill=tk.BOTH, expand=True, padx=20)

        # メタ情報（気分・更新日時）
        self.meta_header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 気分
        mood_icon = "😐"
        mood_text = "Neutral"
        mood_color = "#757575"
        
        if record.mood == "good":
            mood_icon = "😊"
            mood_text = "Good"
            mood_color = "#4CAF50"
        elif record.mood == "bad":
            mood_icon = "😞"
            mood_text = "Bad"
            mood_color = "#F44336"
            
        if record.mood:
            self.mood_label.config(text=f"{mood_icon} {mood_text}", foreground=mood_color)
            self.mood_label.pack(side=tk.LEFT)
        else:
            self.mood_label.pack_forget()

        # 更新日時
        updated_text = f"最終更新: {record.updated_at}"
        self.updated_label.config(text=updated_text)
        self.updated_label.pack(side=tk.RIGHT, anchor=tk.S)

        # タグ（チップ表示）
        # 既存のタグをクリア
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
            
        if record.tags:
            self.tags_frame.pack(fill=tk.X, pady=(0, 15))
            for tag in record.tags:
                tag_label = tk.Label(
                    self.tags_frame,
                    text=f"# {tag}",
                    bg="#E3F2FD",  # 薄い青背景
                    fg="#1565C0",  # 濃い青文字
                    font=("Yu Gothic UI", 9),
                    padx=10,
                    pady=2,
                    relief="flat"
                )
                tag_label.pack(side=tk.LEFT, padx=(0, 5))
        else:
            self.tags_frame.pack_forget()

        # テキスト表示
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", record.text if record.text else "")
        # 少し行間を空ける
        self.text_area.tag_configure("all", spacing1=5, spacing2=2)
        self.text_area.tag_add("all", "1.0", "end")
        self.text_area.config(state=tk.DISABLED)

        # 画像表示
        if record.images:
            self.image_frame.pack(fill=tk.BOTH, pady=(0, 10))
            self.image_header.pack(anchor=tk.W, pady=(0, 10))
            self.image_container.pack(fill=tk.X)

            # 既存の画像をクリア
            for widget in self.image_container.winfo_children():
                widget.destroy()

            # 画像を並べて表示
            for idx, image in enumerate(record.images):
                img_frame = ttk.Frame(self.image_container, style="Card.TFrame")
                img_frame.pack(side=tk.LEFT, padx=(0, 10), pady=5)

                # サムネイル表示
                try:
                    if os.path.exists(image.thumbnail_path):
                        img = Image.open(image.thumbnail_path)
                        img.thumbnail((150, 150)) # 少し大きく
                        photo = ImageTk.PhotoImage(img)
                        self.thumbnail_refs.append(photo)

                        img_label = ttk.Label(img_frame, image=photo, cursor="hand2", style="Card.TLabel")
                        img_label.pack()

                        # クリックで拡大表示
                        img_label.bind("<Button-1>", lambda e, path=image.path: self._show_full_image(path))
                    else:
                        ttk.Label(img_frame, text="画像なし", style="Card.TLabel").pack()
                except Exception as e:
                    ttk.Label(img_frame, text="読込エラー", style="Card.TLabel").pack()

                # キャプション
                if image.caption:
                    caption_label = ttk.Label(
                        img_frame,
                        text=image.caption[:20] + "..." if len(image.caption) > 20 else image.caption,
                        font=("Yu Gothic UI", 8),
                        style="Card.TLabel"
                    )
                    caption_label.pack(pady=(2, 0))
        else:
            self.image_frame.pack_forget()


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
