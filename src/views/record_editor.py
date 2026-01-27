"""記録編集ビュー"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from PIL import Image, ImageTk
import os


class RecordEditor:
    """記録の作成・編集画面"""

    def __init__(self, parent, record_controller, date, on_save=None):
        self.parent = parent
        self.record_controller = record_controller
        self.date = date
        self.on_save = on_save

        # 既存の記録を読み込み
        self.record = self.record_controller.get_record(date)

        # 画像サムネイル表示用
        self.image_thumbnails = []
        self.thumbnail_refs = []  # ImageTkのガベージコレクション防止

        self._create_widgets()
        self._layout_widgets()
        self._load_record()

    def _create_widgets(self):
        """ウィジェットを作成"""
        # メインフレーム
        self.main_frame = ttk.Frame(self.parent, padding=10)

        # テキスト入力エリア
        self.text_frame = ttk.LabelFrame(self.main_frame, text="記録テキスト（普通のテキストでOK、Markdownも使えます）", padding=10)
        self.text_area = scrolledtext.ScrolledText(
            self.text_frame,
            wrap=tk.WORD,
            width=70,
            height=15,
            font=("", 10)
        )

        # タグ入力
        self.tags_frame = ttk.Frame(self.main_frame)
        ttk.Label(self.tags_frame, text="タグ (カンマ区切り):").pack(side=tk.LEFT, padx=(0, 5))
        self.tags_entry = ttk.Entry(self.tags_frame, width=40)
        self.tags_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 気分選択
        self.mood_frame = ttk.Frame(self.main_frame)
        ttk.Label(self.mood_frame, text="気分:").pack(side=tk.LEFT, padx=(0, 5))
        self.mood_var = tk.StringVar(value="")
        self.mood_combo = ttk.Combobox(
            self.mood_frame,
            textvariable=self.mood_var,
            values=["", "good", "neutral", "bad"],
            state="readonly",
            width=15
        )
        self.mood_combo.pack(side=tk.LEFT)

        # 画像エリア
        self.image_frame = ttk.LabelFrame(self.main_frame, text="添付画像", padding=10)

        # 画像リストフレーム（スクロール可能）
        self.image_list_canvas = tk.Canvas(self.image_frame, height=150)
        self.image_list_scrollbar = ttk.Scrollbar(
            self.image_frame,
            orient=tk.HORIZONTAL,
            command=self.image_list_canvas.xview
        )
        self.image_list_canvas.configure(xscrollcommand=self.image_list_scrollbar.set)

        self.image_list_frame = ttk.Frame(self.image_list_canvas)
        self.image_list_canvas.create_window((0, 0), window=self.image_list_frame, anchor=tk.NW)

        # 画像追加ボタン
        self.add_image_button = ttk.Button(
            self.image_frame,
            text="画像を追加",
            command=self._add_image
        )

        # ボタンエリア
        self.button_frame = ttk.Frame(self.main_frame)
        self.save_button = ttk.Button(
            self.button_frame,
            text="保存",
            command=self._save_record
        )
        self.delete_button = ttk.Button(
            self.button_frame,
            text="削除",
            command=self._delete_record
        )
        self.cancel_button = ttk.Button(
            self.button_frame,
            text="キャンセル",
            command=self.parent.destroy
        )

    def _layout_widgets(self):
        """ウィジェットをレイアウト"""
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # テキストエリア
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # タグと気分
        self.tags_frame.pack(fill=tk.X, pady=(0, 5))
        self.mood_frame.pack(fill=tk.X, pady=(0, 10))

        # 画像エリア
        self.image_frame.pack(fill=tk.BOTH, pady=(0, 10))
        self.image_list_canvas.pack(fill=tk.BOTH, expand=True)
        self.image_list_scrollbar.pack(fill=tk.X)
        self.add_image_button.pack(pady=(5, 0))

        # ボタン
        self.button_frame.pack(fill=tk.X)
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        self.delete_button.pack(side=tk.LEFT, padx=(0, 5))
        self.cancel_button.pack(side=tk.RIGHT)

    def _load_record(self):
        """既存の記録を読み込み"""
        if self.record:
            self.text_area.insert("1.0", self.record.text)
            self.tags_entry.insert(0, ", ".join(self.record.tags))
            if self.record.mood:
                self.mood_var.set(self.record.mood)

            # 画像を表示
            self._refresh_image_list()

    def _refresh_image_list(self):
        """画像リストを更新"""
        # 既存のウィジェットをクリア
        for widget in self.image_list_frame.winfo_children():
            widget.destroy()
        self.thumbnail_refs.clear()

        if not self.record or not self.record.images:
            return

        # 画像を横に並べて表示
        for idx, image in enumerate(self.record.images):
            image_frame = ttk.Frame(self.image_list_frame, relief=tk.RAISED, borderwidth=1)
            image_frame.pack(side=tk.LEFT, padx=5, pady=5)

            # サムネイル表示
            try:
                if os.path.exists(image.thumbnail_path):
                    img = Image.open(image.thumbnail_path)
                    img.thumbnail((100, 100))
                    photo = ImageTk.PhotoImage(img)
                    self.thumbnail_refs.append(photo)

                    img_label = ttk.Label(image_frame, image=photo)
                    img_label.pack()
                else:
                    ttk.Label(image_frame, text="画像なし").pack()
            except Exception as e:
                ttk.Label(image_frame, text="読込エラー").pack()

            # ファイル名
            ttk.Label(
                image_frame,
                text=image.filename[:20] + "..." if len(image.filename) > 20 else image.filename,
                font=("", 8)
            ).pack()

            # 削除ボタン
            delete_btn = ttk.Button(
                image_frame,
                text="削除",
                command=lambda img_id=image.id: self._remove_image(img_id),
                width=8
            )
            delete_btn.pack(pady=(2, 0))

        # スクロール領域を更新
        self.image_list_frame.update_idletasks()
        self.image_list_canvas.configure(scrollregion=self.image_list_canvas.bbox("all"))

    def _add_image(self):
        """画像を追加"""
        filetypes = [
            ("画像ファイル", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("すべてのファイル", "*.*")
        ]
        file_path = filedialog.askopenfilename(
            title="画像を選択",
            filetypes=filetypes
        )

        if file_path:
            success, message, image_attachment = self.record_controller.add_image_to_record(
                self.date,
                file_path
            )

            if success:
                # 記録を再読み込み
                self.record = self.record_controller.get_record(self.date)
                self._refresh_image_list()
                messagebox.showinfo("成功", "画像を追加しました")
            else:
                messagebox.showerror("エラー", f"画像追加失敗:\n{message}")

    def _remove_image(self, image_id: str):
        """画像を削除"""
        if messagebox.askyesno("確認", "この画像を削除しますか？"):
            success, message = self.record_controller.remove_image_from_record(self.date, image_id)

            if success:
                self.record = self.record_controller.get_record(self.date)
                self._refresh_image_list()
                messagebox.showinfo("成功", "画像を削除しました")
            else:
                messagebox.showerror("エラー", f"画像削除失敗:\n{message}")

    def _save_record(self):
        """記録を保存"""
        text = self.text_area.get("1.0", tk.END).strip()
        tags_str = self.tags_entry.get().strip()
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        mood = self.mood_var.get() if self.mood_var.get() else None

        if self.record:
            # 更新
            self.record_controller.update_record(self.date, text, tags, mood)
        else:
            # 新規作成
            self.record_controller.create_record(self.date, text, tags, mood)

        messagebox.showinfo("成功", "記録を保存しました")

        if self.on_save:
            self.on_save()

        self.parent.destroy()

    def _delete_record(self):
        """記録を削除"""
        if not self.record:
            messagebox.showwarning("警告", "記録が存在しません")
            return

        if messagebox.askyesno("確認", "この記録を削除しますか？\n（関連する画像も削除されます）"):
            if self.record_controller.delete_record(self.date):
                messagebox.showinfo("成功", "記録を削除しました")

                if self.on_save:
                    self.on_save()

                self.parent.destroy()
            else:
                messagebox.showerror("エラー", "記録の削除に失敗しました")
