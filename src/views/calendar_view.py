import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar
import os
from PIL import Image, ImageTk
from .styles import AppStyles


class CalendarView:
    """カレンダー表示と日付選択"""

    def __init__(self, parent, record_controller, on_date_select=None):
        self.parent = parent
        self.record_controller = record_controller
        self.on_date_select = on_date_select

        # 現在表示中の年月
        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date = today.strftime("%Y-%m-%d")

        # 画像参照保持用
        self.calendar_images = []

        self._create_widgets()
        self._layout_widgets()
        self._draw_calendar()

    def _create_widgets(self):
        """ウィジェットを作成"""
        # メインコンテナ
        self.container = ttk.Frame(self.parent, style="Card.TFrame")
        self.container.pack(fill=tk.BOTH, expand=True)

        # ナビゲーションフレーム
        self.nav_frame = ttk.Frame(self.container, style="Card.TFrame")

        self.prev_button = ttk.Button(
            self.nav_frame,
            text="<",
            width=3,
            command=self._prev_month,
            style="TButton"
        )

        self.today_button = ttk.Button(
            self.nav_frame,
            text="今日",
            command=self._goto_today,
            style="TButton"
        )

        self.next_button = ttk.Button(
            self.nav_frame,
            text=">",
            width=3,
            command=self._next_month,
            style="TButton"
        )

        # 年月表示
        self.month_label = ttk.Label(
            self.container,
            text=self._get_month_label(),
            font=("Yu Gothic UI", 14, "bold"),
            style="Card.TLabel",
            anchor="center"
        )

        # カレンダーグリッドフレーム
        self.calendar_frame = ttk.Frame(self.container, style="Card.TFrame")

    def _layout_widgets(self):
        """ウィジェットをレイアウト"""
        self.nav_frame.pack(fill=tk.X, pady=(0, 15))
        self.prev_button.pack(side=tk.LEFT)
        self.today_button.pack(side=tk.LEFT, padx=5)
        self.next_button.pack(side=tk.RIGHT)

        self.month_label.pack(fill=tk.X, pady=(0, 15))
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)

    def _get_month_label(self) -> str:
        """年月のラベルを取得"""
        return f"{self.current_year}年 {self.current_month}月"

    def _draw_calendar(self):
        """カレンダーを描画"""
        # 既存のウィジェットをクリア
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # 画像参照をクリア
        self.calendar_images = []

        # 月のレコードを一括取得
        monthly_records = self.record_controller.get_records_by_month(self.current_year, self.current_month)
        # 日付判定用にキーのセットも持っておく（念のため）
        dates_with_records = set(monthly_records.keys())

        # 曜日ヘッダー
        weekdays = ["日", "月", "火", "水", "木", "金", "土"]
        colors = ["#E91E63", "#757575", "#757575", "#757575", "#757575", "#757575", "#3F51B5"]
        
        for col, (day, color) in enumerate(zip(weekdays, colors)):
            label = ttk.Label(
                self.calendar_frame,
                text=day,
                font=("Yu Gothic UI", 10, "bold"),
                foreground=color,
                anchor=tk.CENTER,
                style="Card.TLabel"
            )
            # ヘッダーは高さ固定
            self.calendar_frame.rowconfigure(0, weight=0)
            label.grid(row=0, column=col, sticky="nsew", pady=(0, 5))

        # カレンダーデータを取得
        cal = calendar.monthcalendar(self.current_year, self.current_month)

        # 日付セルを配置
        for row_idx, week in enumerate(cal):
            # 各行の高さを均等に広げる
            self.calendar_frame.rowconfigure(row_idx + 1, weight=1)

            for col_idx, day in enumerate(week):
                # 列の幅を均等に
                self.calendar_frame.columnconfigure(col_idx, weight=1)

                if day == 0:
                    # 空のセル
                    label = ttk.Label(self.calendar_frame, text="", style="Card.TLabel")
                    label.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=1, pady=1)
                    continue

                # 日付情報
                date_str = f"{self.current_year:04d}-{self.current_month:02d}-{day:02d}"
                record = monthly_records.get(date_str)
                has_record = record is not None

                # 今日判定
                today_dt = datetime.now()
                is_today = (
                    self.current_year == today_dt.year and
                    self.current_month == today_dt.month and
                    day == today_dt.day
                )

                # 選択中判定
                is_selected = date_str == self.selected_date

                # スタイル決定
                bg_color = AppStyles.COLOR_SURFACE
                fg_color = AppStyles.COLOR_TEXT
                border_color = "#E0E0E0" # 薄いグレー
                border_width = 1

                if is_selected:
                    bg_color = "#E8EAF6" # 薄いインディゴ背景
                    border_color = AppStyles.COLOR_PRIMARY
                    border_width = 2
                elif is_today:
                    bg_color = "#E3F2FD" # 薄い青
                elif has_record:
                    bg_color = "#F1F8E9" # ごく薄い緑
                
                # 土日の文字色
                date_fg_color = fg_color
                if col_idx == 0: # 日
                    date_fg_color = "#E91E63"
                elif col_idx == 6: # 土
                    date_fg_color = "#3F51B5"

                # セルコンテナ (Frame)
                # tk.Frameを使って背景色を細かく制御
                cell_frame = tk.Frame(
                    self.calendar_frame,
                    bg=border_color, # ボーダー色として使用
                    bd=0
                )
                cell_frame.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=1, pady=1)

                # コンテンツエリア (内側のFrame)
                content_frame = tk.Frame(
                    cell_frame,
                    bg=bg_color
                )
                # ボーダー幅分だけ内側に配置
                content_frame.pack(fill=tk.BOTH, expand=True, padx=border_width, pady=border_width)

                # クリックイベントのハンドラ
                def on_click(e, d=date_str):
                    self._on_date_clicked(d)

                # 全要素にクリックイベントをバインド
                cell_frame.bind("<Button-1>", on_click)
                content_frame.bind("<Button-1>", on_click)

                # 日付表示
                day_label = tk.Label(
                    content_frame,
                    text=str(day),
                    font=("Yu Gothic UI", 9, "bold" if is_today or is_selected else "normal"),
                    fg=date_fg_color,
                    bg=bg_color,
                    anchor="nw"
                )
                day_label.pack(side=tk.TOP, anchor="nw", padx=2)
                day_label.bind("<Button-1>", on_click)

                # --- 記録内容の表示 ---
                if record:
                    # 画像があれば表示（サムネイル）
                    if record.images:
                        try:
                            # 最初の画像のサムネイルを使用
                            thumb_path = record.images[0].thumbnail_path
                            if os.path.exists(thumb_path):
                                img = Image.open(thumb_path)
                                # 小さくリサイズ (アスペクト比維持)
                                img.thumbnail((50, 50)) 
                                photo = ImageTk.PhotoImage(img)
                                self.calendar_images.append(photo) # 参照保持

                                img_label = tk.Label(content_frame, image=photo, bg=bg_color)
                                img_label.pack(side=tk.TOP, pady=1)
                                img_label.bind("<Button-1>", on_click)
                        except Exception:
                            pass # 画像読み込み失敗時は無視

                    # テキストがあれば表示（省略）
                    if record.text:
                        short_text = record.text.strip().replace("\n", " ")
                        if len(short_text) > 0:
                            # 文字数制限
                            limit = 6
                            if len(short_text) > limit:
                                short_text = short_text[:limit] + ".."
                            
                            text_label = tk.Label(
                                content_frame,
                                text=short_text,
                                font=("Yu Gothic UI", 8),
                                fg="#555555",
                                bg=bg_color,
                                anchor="w"
                            )
                            text_label.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=1)
                            text_label.bind("<Button-1>", on_click)

    def _on_date_clicked(self, date: str):
        """日付がクリックされた時"""
        self.selected_date = date
        self._draw_calendar()

        if self.on_date_select:
            self.on_date_select(date)

    def _prev_month(self):
        """前月へ移動"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1

        self.month_label.config(text=self._get_month_label())
        self.refresh()

    def _next_month(self):
        """次月へ移動"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1

        self.month_label.config(text=self._get_month_label())
        self.refresh()

    def _goto_today(self):
        """今日の日付へジャンプ"""
        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date = today.strftime("%Y-%m-%d")

        self.month_label.config(text=self._get_month_label())
        self.refresh()

        if self.on_date_select:
            self.on_date_select(self.selected_date)

    def refresh(self):
        """カレンダーを更新"""
        self.dates_with_records = set(self.record_controller.get_dates_with_records())
        self._draw_calendar()
