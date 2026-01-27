"""カレンダービュー"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar


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
        # ナビゲーションフレーム
        self.nav_frame = ttk.Frame(self.parent)

        self.prev_button = ttk.Button(
            self.nav_frame,
            text="<",
            width=3,
            command=self._prev_month
        )

        self.today_button = ttk.Button(
            self.nav_frame,
            text="今日",
            command=self._goto_today
        )

        self.next_button = ttk.Button(
            self.nav_frame,
            text=">",
            width=3,
            command=self._next_month
        )

        # 年月表示
        self.month_label = ttk.Label(
            self.parent,
            text=self._get_month_label(),
            font=("", 12, "bold")
        )

        # カレンダーグリッドフレーム
        self.calendar_frame = ttk.Frame(self.parent)

    def _layout_widgets(self):
        """ウィジェットをレイアウト"""
        self.nav_frame.pack(fill=tk.X, pady=(0, 10))
        self.prev_button.pack(side=tk.LEFT, padx=2)
        self.today_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.next_button.pack(side=tk.RIGHT, padx=2)

        self.month_label.pack(pady=(0, 10))
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
        for col, day in enumerate(weekdays):
            label = ttk.Label(
                self.calendar_frame,
                text=day,
                font=("", 9, "bold"),
                anchor=tk.CENTER
            )
            label.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        # カレンダーデータを取得
        cal = calendar.monthcalendar(self.current_year, self.current_month)

        # 日付ボタンを配置
        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    # 空のセル
                    label = ttk.Label(self.calendar_frame, text="")
                    label.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=1, pady=1)
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

                    button = tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        width=4,
                        height=2,
                        command=lambda d=date_str: self._on_date_clicked(d)
                    )

                    # スタイル設定
                    if is_selected:
                        button.config(bg="#4A90E2", fg="white", font=("", 9, "bold"))
                    elif is_today:
                        button.config(bg="#E8F4F8", font=("", 9, "bold"))
                    elif has_record:
                        button.config(bg="#D4EDDA", font=("", 9))
                    else:
                        button.config(bg="white", font=("", 9))

                    # 日曜日は赤、土曜日は青
                    if col_idx == 0 and not is_selected:  # 日曜日
                        button.config(fg="red")
                    elif col_idx == 6 and not is_selected:  # 土曜日
                        button.config(fg="blue")

                    button.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=1, pady=1)

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
