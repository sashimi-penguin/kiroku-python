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
        # メインフレーム（全体）
        self.main_frame = ttk.Frame(self.root)

        # --- ヘッダーエリア ---
        self.header_frame = ttk.Frame(self.main_frame)
        self.app_title = ttk.Label(
            self.header_frame,
            text="Record Keeper",
            style="Header.TLabel"
        )
        self.current_date_label = ttk.Label(
            self.header_frame,
            text=f"{datetime.now().strftime('%Y年%m月%d日')}",
            font=("", 10),
            foreground="#757575"
        )

        # --- コンテンツエリア（左右分割）---
        self.content_frame = ttk.Frame(self.main_frame)

        # 左側: カレンダー（カードスタイル）
        self.left_panel = ttk.Frame(self.content_frame, style="Card.TFrame", padding=15)
        # 影のようなボーダー効果（オプション）
        self.left_panel_border = ttk.Frame(self.content_frame, style="TFrame") 
        
        self.calendar_header_label = ttk.Label(
            self.left_panel, 
            text="CALENDAR", 
            style="CardHeader.TLabel"
        )
        
        self.calendar_view = CalendarView(
            self.left_panel,
            self.record_controller,
            on_date_select=self._on_date_selected
        )

        # 右側: 詳細・表示エリア
        self.right_panel = ttk.Frame(self.content_frame, style="Card.TFrame", padding=20)
        
        # 日付見出し
        self.date_header_frame = ttk.Frame(self.right_panel, style="Card.TFrame")
        self.date_label = ttk.Label(
            self.date_header_frame,
            text=self._format_date(self.selected_date),
            style="CardHeader.TLabel",
            font=("Yu Gothic UI", 16, "bold")
        )
        
        # 操作ボタン（右揃え）
        self.button_frame = ttk.Frame(self.date_header_frame, style="Card.TFrame")
        self.edit_button = ttk.Button(
            self.button_frame,
            text="✎ 編集する",
            command=self._open_editor,
            style="Primary.TButton"
        )
        self.export_button = ttk.Button(
            self.button_frame,
            text="↓ エクスポート",
            command=self._export_markdown,
            style="TButton"
        )

        # 記録ビューアーエリア
        self.viewer_container = ttk.Frame(self.right_panel, style="Card.TFrame")
        self.record_viewer = RecordViewer(self.viewer_container, self.record_controller)

    def _layout_widgets(self):
        """ウィジェットをレイアウト"""
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ヘッダー配置
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        self.app_title.pack(side=tk.LEFT)
        self.current_date_label.pack(side=tk.RIGHT, anchor=tk.S, pady=(0, 5))

        # コンテンツエリア配置
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # カレンダー（左）
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        self.calendar_header_label.pack(anchor=tk.W, pady=(0, 15))
        # CalendarView自体は内部でpackする想定だが、ラップが必要ならここで行う

        # 詳細エリア（右）
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        
        # 右側パネル内のレイアウト
        self.date_header_frame.pack(fill=tk.X, pady=(0, 15))
        self.date_label.pack(side=tk.LEFT)
        
        self.button_frame.pack(side=tk.RIGHT)
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        self.edit_button.pack(side=tk.LEFT)
        
        ttk.Separator(self.right_panel, orient="horizontal").pack(fill=tk.X, pady=(0, 15))
        
        self.viewer_container.pack(fill=tk.BOTH, expand=True)

        # グリッドの重み設定
        self.content_frame.columnconfigure(0, weight=4)  # カレンダー幅
        self.content_frame.columnconfigure(1, weight=6)  # 詳細幅
        self.content_frame.rowconfigure(0, weight=1)

    def _format_date(self, date_str):
        """日付文字列を整形 (YYYY-MM-DD -> YYYY年MM月DD日)"""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%Y年%m月%d日")
        except:
            return date_str

    def _on_date_selected(self, date: str):
        """カレンダーで日付が選択された時"""
        self.selected_date = date
        self.date_label.config(text=self._format_date(self.selected_date))
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
