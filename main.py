"""毎日の記録ツール - エントリーポイント"""
import sys
import os

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import App


def main():
    """メイン関数"""
    try:
        app = App()
        app.run()
    except Exception as e:
        print(f"アプリケーションエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
