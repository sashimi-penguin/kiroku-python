import tkinter as tk
from tkinter import ttk

class AppStyles:
    """アプリケーション全体のスタイル定義"""
    
    # カラーパレット
    COLOR_PRIMARY = "#3F51B5"      # インディゴ
    COLOR_PRIMARY_DARK = "#303F9F"
    COLOR_ACCENT = "#FF4081"       # ピンク
    COLOR_BACKGROUND = "#F5F5F7"   # 背景色（オフホワイト）
    COLOR_SURFACE = "#FFFFFF"      # カード背景（白）
    COLOR_TEXT = "#333333"         # メインテキスト
    COLOR_TEXT_LIGHT = "#757575"   # サブテキスト
    COLOR_BORDER = "#E0E0E0"       # 境界線
    
    # フォント設定
    FONT_FAMILY = "Yu Gothic UI"  # Windows標準の読みやすいフォント
    FONT_HEADER = (FONT_FAMILY, 18, "bold")
    FONT_SUBHEADER = (FONT_FAMILY, 14, "bold")
    FONT_BODY = (FONT_FAMILY, 10)
    FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
    FONT_SMALL = (FONT_FAMILY, 9)

    @staticmethod
    def setup_styles(root):
        """スタイルを初期化して適用"""
        style = ttk.Style(root)
        
        # ベーステーマを設定（'clam'はカスタマイズしやすい）
        try:
            style.theme_use('clam')
        except:
            pass  # clamがない場合はデフォルトを使用
        
        # ルートウィンドウの背景
        root.configure(bg=AppStyles.COLOR_BACKGROUND)
        
        # --- 共通設定 ---
        
        # TFrame: デフォルトは背景色と同じ
        style.configure("TFrame", background=AppStyles.COLOR_BACKGROUND)
        
        # Card: 白背景のコンテナ用
        style.configure("Card.TFrame", background=AppStyles.COLOR_SURFACE)
        
        # TLabel: デフォルト
        style.configure("TLabel", 
                        background=AppStyles.COLOR_BACKGROUND, 
                        foreground=AppStyles.COLOR_TEXT,
                        font=AppStyles.FONT_BODY)
        
        # Header: 大見出し
        style.configure("Header.TLabel", 
                        font=AppStyles.FONT_HEADER, 
                        background=AppStyles.COLOR_BACKGROUND,
                        foreground=AppStyles.COLOR_PRIMARY)
        
        # Card内のラベル
        style.configure("Card.TLabel", 
                        background=AppStyles.COLOR_SURFACE,
                        foreground=AppStyles.COLOR_TEXT)
        
        # Card内の見出し
        style.configure("CardHeader.TLabel",
                        background=AppStyles.COLOR_SURFACE,
                        font=AppStyles.FONT_SUBHEADER,
                        foreground=AppStyles.COLOR_PRIMARY)
        
        # --- ボタン設定 ---
        
        # 通常ボタン
        style.configure("TButton", 
                        font=AppStyles.FONT_BODY, 
                        background=AppStyles.COLOR_SURFACE, 
                        foreground=AppStyles.COLOR_TEXT,
                        borderwidth=1,
                        focusthickness=0,
                        focuscolor="none")
        style.map("TButton", 
                  background=[('active', AppStyles.COLOR_BORDER)],
                  foreground=[('active', AppStyles.COLOR_TEXT)])
        
        # プライマリボタン（強調）
        style.configure("Primary.TButton", 
                        font=AppStyles.FONT_BODY_BOLD,
                        background=AppStyles.COLOR_PRIMARY, 
                        foreground="#FFFFFF",  # 白文字
                        borderwidth=0)
        style.map("Primary.TButton",
                  background=[('active', AppStyles.COLOR_PRIMARY_DARK)],
                  foreground=[('active', "#FFFFFF")])
                  
        # アクセントボタン（さらに強調）
        style.configure("Accent.TButton", 
                        font=AppStyles.FONT_BODY_BOLD,
                        background=AppStyles.COLOR_ACCENT, 
                        foreground="#FFFFFF",
                        borderwidth=0)
        style.map("Accent.TButton",
                  background=[('active', "#C2185B")],
                  foreground=[('active', "#FFFFFF")])

        # --- LabelFrame設定 ---
        
        style.configure("TLabelframe", 
                        background=AppStyles.COLOR_BACKGROUND, 
                        borderwidth=1,
                        relief="solid")
        style.configure("TLabelframe.Label", 
                        background=AppStyles.COLOR_BACKGROUND, 
                        foreground=AppStyles.COLOR_TEXT_LIGHT,
                        font=AppStyles.FONT_BODY_BOLD)
                        
        # Card内のLabelFrame
        style.configure("Card.TLabelframe",
                        background=AppStyles.COLOR_SURFACE,
                        borderwidth=0)
        style.configure("Card.TLabelframe.Label",
                        background=AppStyles.COLOR_SURFACE,
                        foreground=AppStyles.COLOR_PRIMARY,
                        font=AppStyles.FONT_BODY_BOLD)

        # Scrollbar
        style.configure("TScrollbar",
                        background=AppStyles.COLOR_BACKGROUND,
                        troughcolor=AppStyles.COLOR_BACKGROUND,
                        borderwidth=0,
                        arrowsize=12)

        return style
