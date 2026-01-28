"""アプリケーションメインクラス"""
import tkinter as tk
from tkinter import messagebox
import os
from .controllers.record_controller import RecordController
from .views.main_window import MainWindow
from .views.styles import AppStyles


class App:
    """アプリケーションの初期化と実行"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("毎日の記録ツール")
        self.root.geometry("1100x750")  # サイズを少し大きくする

        # スタイルの適用
        AppStyles.setup_styles(self.root)

        # ディレクトリ構造を初期化
        self._initialize_directories()

        # コントローラーの初期化
        self.record_controller = RecordController()

        # メインウィンドウの作成
        self.main_window = MainWindow(self.root, self.record_controller)

        # ウィンドウを閉じる時の処理
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _initialize_directories(self):
        """必要なディレクトリを作成"""
        directories = [
            "data",
            "data/images",
            "exports"
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def _on_closing(self):
        """アプリケーション終了時の処理"""
        if messagebox.askokcancel("終了", "アプリケーションを終了しますか？"):
            self.root.destroy()

    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()
