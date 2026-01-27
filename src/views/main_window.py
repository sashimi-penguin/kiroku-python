"""メインウィンドウ"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from .calendar_view import CalendarView
from .record_viewer import RecordViewer
from .record_editor import RecordEditor
from ..controllers.export_controller import ExportController


class MainWindow:
    """アプリケーションのメインウィンドウ"""

    def __init__(self, root, record_controller):
        self.root = root
        self.record_controller = record_controller
        self.export_controller = ExportController(record_controller)
        self.selected_date = datetime.now().strftime("%Y-%m-%d")

        self._create_widgets()
        self._layout_widgets()

        # 初期表示
        self._refresh_viewer()

    def _create_widgets(self):
        """ウィジェットを作成"""
        # メインフレーム
        self.main_frame = ttk.Frame(self.root)

        # 左側: カレンダービュー
        self.calendar_frame = ttk.LabelFrame(self.main_frame, text="カレンダー", padding=10)
        self.calendar_view = CalendarView(
            self.calendar_frame,
            self.record_controller,
            on_date_select=self._on_date_selected
        )

        # 右側: 記録表示・編集エリア
        self.right_frame = ttk.Frame(self.main_frame)

        # 選択日表示
        self.date_label_frame = ttk.Frame(self.right_frame)
        self.date_label = ttk.Label(
            self.date_label_frame,
            text=f"選択日: {self.selected_date}",
            font=("", 14, "bold")
        )

        # ボタンフレーム
        self.button_frame = ttk.Frame(self.right_frame)
        self.edit_button = ttk.Button(
            self.button_frame,
            text="記録を追加/編集",
            command=self._open_editor
        )
        self.export_button = ttk.Button(
            self.button_frame,
            text="Markdownエクスポート",
            command=self._export_markdown
        )

        # 記録ビューアー
        self.viewer_frame = ttk.LabelFrame(self.right_frame, text="記録プレビュー", padding=10)
        self.record_viewer = RecordViewer(self.viewer_frame, self.record_controller)

    def _layout_widgets(self):
        """ウィジェットをレイアウト"""
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左側カレンダー（30%）
        self.calendar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # 右側エリア（70%）
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # グリッドの重み設定
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=7)
        self.main_frame.rowconfigure(0, weight=1)

        # 右側エリアのレイアウト
        self.date_label_frame.pack(fill=tk.X, pady=(0, 10))
        self.date_label.pack(side=tk.LEFT)

        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        self.edit_button.pack(side=tk.LEFT, padx=(0, 5))
        self.export_button.pack(side=tk.LEFT)

        self.viewer_frame.pack(fill=tk.BOTH, expand=True)

        # 右側エリアの内部レイアウト
        self.right_frame.rowconfigure(2, weight=1)

    def _on_date_selected(self, date: str):
        """カレンダーで日付が選択された時"""
        self.selected_date = date
        self.date_label.config(text=f"選択日: {self.selected_date}")
        self._refresh_viewer()

    def _refresh_viewer(self):
        """記録ビューアーを更新"""
        self.record_viewer.display_record(self.selected_date)

    def _open_editor(self):
        """記録エディターを開く"""
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"記録編集 - {self.selected_date}")
        editor_window.geometry("800x600")

        editor = RecordEditor(
            editor_window,
            self.record_controller,
            self.selected_date,
            on_save=self._on_record_saved
        )

    def _on_record_saved(self):
        """記録が保存された時"""
        self._refresh_viewer()
        self.calendar_view.refresh()

    def _export_markdown(self):
        """Markdown形式でエクスポート"""
        if not self.record_controller.record_exists(self.selected_date):
            messagebox.showwarning("警告", "選択した日付に記録がありません")
            return

        success, message, filepath = self.export_controller.export_single_record(self.selected_date)
        if success:
            messagebox.showinfo("成功", f"エクスポートしました:\n{filepath}")
        else:
            messagebox.showerror("エラー", f"エクスポート失敗:\n{message}")
