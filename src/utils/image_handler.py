"""画像処理ユーティリティ"""
import os
import shutil
from typing import Tuple, Optional
from PIL import Image
import uuid
from datetime import datetime


class ImageHandler:
    """画像の保存・サムネイル生成・削除を管理"""

    THUMBNAIL_SIZE = (200, 200)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

    def __init__(self, base_dir: str = "data/images"):
        self.base_dir = base_dir

    def _get_year_month_dir(self, year: int, month: int) -> str:
        """年月ディレクトリのパスを取得"""
        return os.path.join(self.base_dir, f"{year:04d}", f"{month:02d}")

    def _ensure_directory(self, directory: str):
        """ディレクトリの存在を確認・作成"""
        os.makedirs(directory, exist_ok=True)

    def validate_image(self, file_path: str) -> Tuple[bool, str]:
        """画像ファイルの検証"""
        # ファイル存在チェック
        if not os.path.exists(file_path):
            return False, "ファイルが存在しません"

        # 拡張子チェック
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            return False, f"サポートされていない形式です。対応形式: {', '.join(self.SUPPORTED_FORMATS)}"

        # サイズチェック
        file_size = os.path.getsize(file_path)
        if file_size > self.MAX_IMAGE_SIZE:
            return False, f"ファイルサイズが大きすぎます（最大10MB）。現在: {file_size / 1024 / 1024:.2f}MB"

        # PIL で開けるか確認
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True, "OK"
        except Exception as e:
            return False, f"画像ファイルが破損しています: {str(e)}"

    def save_image(self, source_path: str, date: str) -> Tuple[Optional[str], Optional[str], int, str]:
        """
        画像を保存してサムネイルを生成

        Args:
            source_path: 元画像のパス
            date: 記録日（YYYY-MM-DD）

        Returns:
            (保存先パス, サムネイルパス, ファイルサイズ, エラーメッセージ)
        """
        # 検証
        is_valid, message = self.validate_image(source_path)
        if not is_valid:
            return None, None, 0, message

        try:
            # 日付から年月を抽出
            year, month, _ = map(int, date.split('-'))
            target_dir = self._get_year_month_dir(year, month)
            self._ensure_directory(target_dir)

            # ファイル名生成（UUID）
            image_id = str(uuid.uuid4())
            ext = os.path.splitext(source_path)[1].lower()
            filename = f"{image_id}{ext}"
            thumb_filename = f"{image_id}_thumb{ext}"

            # 保存先パス
            target_path = os.path.join(target_dir, filename)
            thumb_path = os.path.join(target_dir, thumb_filename)

            # 画像をコピー
            shutil.copy2(source_path, target_path)
            file_size = os.path.getsize(target_path)

            # サムネイル生成
            with Image.open(target_path) as img:
                # RGBに変換（透過PNG対応）
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # サムネイル作成（アスペクト比維持）
                img.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                img.save(thumb_path, quality=85, optimize=True)

            return target_path, thumb_path, file_size, ""

        except Exception as e:
            return None, None, 0, f"画像保存エラー: {str(e)}"

    def delete_image(self, image_path: str, thumbnail_path: str) -> bool:
        """画像とサムネイルを削除"""
        success = True
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        except Exception as e:
            print(f"画像削除エラー: {e}")
            success = False
        return success

    def get_image_info(self, image_path: str) -> dict:
        """画像情報を取得"""
        if not os.path.exists(image_path):
            return {"error": "ファイルが存在しません"}

        try:
            with Image.open(image_path) as img:
                return {
                    "size": img.size,
                    "format": img.format,
                    "mode": img.mode,
                    "file_size": os.path.getsize(image_path)
                }
        except Exception as e:
            return {"error": str(e)}
