"""エクスポート機能の制御"""
from typing import Optional, List
from ..utils.markdown_exporter import MarkdownExporter
from .record_controller import RecordController


class ExportController:
    """エクスポート機能を管理"""

    def __init__(self, record_controller: RecordController, export_dir: str = "exports"):
        self.record_controller = record_controller
        self.exporter = MarkdownExporter(export_dir)

    def export_single_record(self, date: str, output_path: Optional[str] = None) -> tuple[bool, str, str]:
        """
        単一の記録をエクスポート

        Args:
            date: エクスポートする記録の日付
            output_path: 出力先パス（Noneの場合は自動生成）

        Returns:
            (成功フラグ, メッセージ, 出力ファイルパス)
        """
        record = self.record_controller.get_record(date)

        if not record:
            return False, f"{date}の記録が見つかりません", ""

        return self.exporter.export_record(record, output_path)

    def export_all_records(self, output_path: Optional[str] = None) -> tuple[bool, str, str]:
        """
        全ての記録をエクスポート

        Args:
            output_path: 出力先パス（Noneの場合は自動生成）

        Returns:
            (成功フラグ, メッセージ, 出力ファイルパス)
        """
        records_dict = self.record_controller.get_all_records()

        if not records_dict:
            return False, "エクスポートする記録がありません", ""

        records_list = list(records_dict.values())
        return self.exporter.export_records(records_list, output_path)

    def export_month(self, year: int, month: int) -> tuple[bool, str, str]:
        """
        特定月の記録をエクスポート

        Args:
            year: 年
            month: 月

        Returns:
            (成功フラグ, メッセージ, 出力ファイルパス)
        """
        records_dict = self.record_controller.get_records_by_month(year, month)

        if not records_dict:
            return False, f"{year}年{month}月の記録がありません", ""

        records_list = list(records_dict.values())
        return self.exporter.export_month(records_list, year, month)

    def export_date_range(self, start_date: str, end_date: str, output_path: Optional[str] = None) -> tuple[bool, str, str]:
        """
        日付範囲で記録をエクスポート

        Args:
            start_date: 開始日（YYYY-MM-DD）
            end_date: 終了日（YYYY-MM-DD）
            output_path: 出力先パス（Noneの場合は自動生成）

        Returns:
            (成功フラグ, メッセージ, 出力ファイルパス)
        """
        all_records = self.record_controller.get_all_records()

        # 日付範囲でフィルタリング
        filtered_records = [
            record for date, record in all_records.items()
            if start_date <= date <= end_date
        ]

        if not filtered_records:
            return False, f"{start_date}から{end_date}の範囲に記録がありません", ""

        return self.exporter.export_records(filtered_records, output_path)

    def export_by_tag(self, tag: str, output_path: Optional[str] = None) -> tuple[bool, str, str]:
        """
        特定タグの記録をエクスポート

        Args:
            tag: タグ名
            output_path: 出力先パス（Noneの場合は自動生成）

        Returns:
            (成功フラグ, メッセージ, 出力ファイルパス)
        """
        all_records = self.record_controller.get_all_records()

        # タグでフィルタリング
        filtered_records = [
            record for record in all_records.values()
            if tag in record.tags
        ]

        if not filtered_records:
            return False, f"タグ '{tag}' を持つ記録がありません", ""

        return self.exporter.export_records(filtered_records, output_path)

    def export_by_mood(self, mood: str, output_path: Optional[str] = None) -> tuple[bool, str, str]:
        """
        特定の気分の記録をエクスポート

        Args:
            mood: 気分（good, neutral, bad）
            output_path: 出力先パス（Noneの場合は自動生成）

        Returns:
            (成功フラグ, メッセージ, 出力ファイルパス)
        """
        all_records = self.record_controller.get_all_records()

        # 気分でフィルタリング
        filtered_records = [
            record for record in all_records.values()
            if record.mood == mood
        ]

        if not filtered_records:
            return False, f"気分 '{mood}' の記録がありません", ""

        return self.exporter.export_records(filtered_records, output_path)
