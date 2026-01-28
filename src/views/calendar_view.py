"""カレンダービュー"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar
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

        # 記録が存在する日付のキャッシュ
        self.dates_with_records = set(self.record_controller.get_dates_with_records())

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
            label.grid(row=0, column=col, sticky="nsew", pady=(0, 5))

        # カレンダーデータを取得
        cal = calendar.monthcalendar(self.current_year, self.current_month)

        # 日付ボタンを配置
        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    # 空のセル
                    label = ttk.Label(self.calendar_frame, text="", style="Card.TLabel")
                    label.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=2, pady=2)
                else:
                    # 日付ボタン
                    date_str = f"{self.current_year:04d}-{self.current_month:02d}-{day:02d}"
                    has_record = date_str in self.dates_with_records

                    # 今日かどうか
                    today = datetime.now()
                    is_today = (
                        self.current_year == today.year and
                        self.current_month == today.month and
                        day == today.day
                    )

                    # 選択された日かどうか
                    is_selected = date_str == self.selected_date

                    # 見た目の設定
                    bg_color = AppStyles.COLOR_SURFACE
                    fg_color = AppStyles.COLOR_TEXT
                    font_style = ("Yu Gothic UI", 10)
                    relief = "flat"
                    bd = 0
                    
                    if is_selected:
                        bg_color = AppStyles.COLOR_PRIMARY
                        fg_color = "white"
                        font_style = ("Yu Gothic UI", 10, "bold")
                    elif is_today:
                        bg_color = "#E3F2FD"      # 薄い青
                        fg_color = AppStyles.COLOR_PRIMARY
                        font_style = ("Yu Gothic UI", 10, "bold")
                        
                    elif has_record:
                        bg_color = "#E8F5E9"      # 薄い緑
                        fg_color = "#2E7D32"

                    # 土日の色調整（選択中以外）
                    if not is_selected and not has_record and not is_today:
                        if col_idx == 0:  # 日
                            fg_color = "#E91E63"
                        elif col_idx == 6:  # 土
                            fg_color = "#3F51B5"

                    # Tkinter標準ボタンを使用（背景色を細かく制御するため）
                    # ただしフラットに見えるように調整
                    button = tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        bg=bg_color,
                        fg=fg_color,
                        font=font_style,
                        relief=relief,
                        borderwidth=bd,
                        activebackground=AppStyles.COLOR_PRIMARY if is_selected else "#EDEDED",
                        activeforeground="white" if is_selected else fg_color,
                        command=lambda d=date_str: self._on_date_clicked(d),
                        cursor="hand2"
                    )
                    
                    # 記録がある場合は下にインジケータ的な装飾を入れたいが、
                    # ボタンだと難しいので、色で表現する方針を維持。
                    
                    # グリッド配置
                    button.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=2, pady=2, ipady=5)

        # グリッドの重み設定
        for i in range(7):
            self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(len(cal) + 1):
            self.calendar_frame.rowconfigure(i, weight=1)

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
