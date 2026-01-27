"""記録のCRUD操作と画像管理を統括"""
from typing import Optional, List, Dict
from ..models.record import Record, ImageAttachment
from ..models.storage import Storage
from ..utils.image_handler import ImageHandler


class RecordController:
    """記録の作成・読取・更新・削除を管理"""

    def __init__(self, data_dir: str = "data"):
        self.storage = Storage(data_dir)
        self.image_handler = ImageHandler()

    def get_record(self, date: str) -> Optional[Record]:
        """指定日の記録を取得"""
        return self.storage.get_record(date)

    def get_all_records(self) -> Dict[str, Record]:
        """全ての記録を取得"""
        return self.storage.get_all_records()

    def get_records_by_month(self, year: int, month: int) -> Dict[str, Record]:
        """指定月の記録を取得"""
        return self.storage.get_records_by_month(year, month)

    def get_dates_with_records(self) -> List[str]:
        """記録が存在する日付のリストを取得"""
        return self.storage.get_dates_with_records()

    def create_record(self, date: str, text: str = "", tags: List[str] = None, mood: Optional[str] = None) -> Record:
        """新規記録を作成"""
        record = Record.create(date, text, tags, mood)
        self.storage.save_record(record)
        return record

    def update_record(self, date: str, text: Optional[str] = None, tags: Optional[List[str]] = None, mood: Optional[str] = None) -> Optional[Record]:
        """記録を更新"""
        record = self.storage.get_record(date)
        if record:
            record.update(text, tags, mood)
            self.storage.save_record(record)
            return record
        return None

    def delete_record(self, date: str) -> bool:
        """記録を削除（関連画像も削除）"""
        record = self.storage.get_record(date)
        if record:
            # 画像ファイルを削除
            for image in record.images:
                self.image_handler.delete_image(image.path, image.thumbnail_path)

            # 記録を削除
            return self.storage.delete_record(date)
        return False

    def record_exists(self, date: str) -> bool:
        """記録が存在するか確認"""
        return self.storage.record_exists(date)

    def add_image_to_record(self, date: str, image_path: str, caption: Optional[str] = None) -> tuple[bool, str, Optional[ImageAttachment]]:
        """
        記録に画像を追加

        Returns:
            (成功フラグ, メッセージ, ImageAttachment)
        """
        # 記録を取得（存在しない場合は作成）
        record = self.storage.get_record(date)
        if not record:
            record = self.create_record(date)

        # 画像を保存
        saved_path, thumb_path, file_size, error = self.image_handler.save_image(image_path, date)
        if error:
            return False, error, None

        # ImageAttachmentを作成
        import os
        filename = os.path.basename(image_path)
        image_attachment = ImageAttachment.create(
            filename=filename,
            path=saved_path,
            thumbnail_path=thumb_path,
            size_bytes=file_size,
            caption=caption
        )

        # 記録に追加
        record.add_image(image_attachment)
        self.storage.save_record(record)

        return True, "画像を追加しました", image_attachment

    def remove_image_from_record(self, date: str, image_id: str) -> tuple[bool, str]:
        """
        記録から画像を削除

        Returns:
            (成功フラグ, メッセージ)
        """
        record = self.storage.get_record(date)
        if not record:
            return False, "記録が見つかりません"

        # 記録から画像を削除
        removed_image = record.remove_image(image_id)
        if not removed_image:
            return False, "画像が見つかりません"

        # ファイルを削除
        self.image_handler.delete_image(removed_image.path, removed_image.thumbnail_path)

        # 記録を保存
        self.storage.save_record(record)

        return True, "画像を削除しました"

    def update_image_caption(self, date: str, image_id: str, caption: str) -> tuple[bool, str]:
        """
        画像のキャプションを更新

        Returns:
            (成功フラグ, メッセージ)
        """
        record = self.storage.get_record(date)
        if not record:
            return False, "記録が見つかりません"

        # 画像を検索
        for image in record.images:
            if image.id == image_id:
                image.caption = caption
                self.storage.save_record(record)
                return True, "キャプションを更新しました"

        return False, "画像が見つかりません"

    def get_metadata(self) -> dict:
        """メタデータを取得"""
        return self.storage.get_metadata()
