"""Markdown形式へのエクスポート"""
import os
from datetime import datetime
from typing import Optional
from ..models.record import Record


class MarkdownExporter:
    """記録をMarkdown形式に変換"""

    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        self._ensure_export_dir()

    def _ensure_export_dir(self):
        """エクスポートディレクトリの存在を確認・作成"""
        os.makedirs(self.export_dir, exist_ok=True)

    def _get_mood_emoji(self, mood: Optional[str]) -> str:
        """気分を絵文字に変換"""
        mood_map = {
            "good": "😊 良い",
            "neutral": "😐 普通",
            "bad": "😞 悪い"
        }
        return mood_map.get(mood, "")

    def export_record(self, record: Record, output_path: Optional[str] = None) -> tuple[bool, str, str]:
        """
        単一の記録をMarkdown形式でエクスポート

        Args:
            record: エクスポートする記録
            output_path: 出力先パス（Noneの場合は自動生成）

        Returns:
            (成功フラグ, メッセージ, 出力ファイルパス)
        """
        try:
            # 出力パスを生成
            if not output_path:
                filename = f"record_{record.date}.md"
                output_path = os.path.join(self.export_dir, filename)

            # Markdown コンテンツを生成
            content = self._generate_markdown(record)

            # ファイルに書き込み
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, "エクスポート成功", output_path

        except Exception as e:
            return False, f"エクスポートエラー: {str(e)}", ""

    def export_records(self, records: list[Record], output_path: Optional[str] = None) -> tuple[bool, str, str]:
        """
        複数の記録をMarkdown形式でエクスポート

        Args:
            records: エクスポートする記録のリスト
            output_path: 出力先パス（Noneの場合は自動生成）

        Returns:
            (成功フラグ, メッセージ, 出力ファイルパス)
        """
        try:
            if not records:
                return False, "エクスポートする記録がありません", ""

            # 出力パスを生成
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"records_export_{timestamp}.md"
                output_path = os.path.join(self.export_dir, filename)

            # Markdown コンテンツを生成
            content_parts = []
            content_parts.append("# 記録エクスポート\n\n")
            content_parts.append(f"**エクスポート日時:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            content_parts.append(f"**記録数:** {len(records)}\n\n")
            content_parts.append("---\n\n")

            # 日付順にソート
            sorted_records = sorted(records, key=lambda r: r.date)

            for record in sorted_records:
                content_parts.append(self._generate_markdown(record))
                content_parts.append("\n---\n\n")

            content = "".join(content_parts)

            # ファイルに書き込み
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, "エクスポート成功", output_path

        except Exception as e:
            return False, f"エクスポートエラー: {str(e)}", ""

    def _generate_markdown(self, record: Record) -> str:
        """単一の記録からMarkdownコンテンツを生成"""
        lines = []

        # タイトル
        lines.append(f"# {record.date}の記録\n\n")

        # メタデータ
        lines.append(f"**作成日時:** {record.created_at}\n\n")

        if record.mood:
            mood_text = self._get_mood_emoji(record.mood)
            lines.append(f"**気分:** {mood_text}\n\n")

        if record.tags:
            tags_text = ", ".join(record.tags)
            lines.append(f"**タグ:** {tags_text}\n\n")

        lines.append("---\n\n")

        # 本文
        if record.text:
            lines.append("## 本文\n\n")
            lines.append(f"{record.text}\n\n")
        else:
            lines.append("*(本文なし)*\n\n")

        # 画像
        if record.images:
            lines.append("---\n\n")
            lines.append("## 添付画像\n\n")

            for idx, image in enumerate(record.images, 1):
                # 相対パスに変換
                rel_path = os.path.relpath(image.path, self.export_dir)

                # キャプション
                if image.caption:
                    lines.append(f"### 画像 {idx}: {image.caption}\n\n")
                else:
                    lines.append(f"### 画像 {idx}\n\n")

                # 画像参照
                lines.append(f"![{image.filename}]({rel_path})\n\n")

                # 画像情報
                size_mb = image.size_bytes / 1024 / 1024
                lines.append(f"*ファイル名:* {image.filename}  \n")
                lines.append(f"*サイズ:* {size_mb:.2f} MB  \n")
                lines.append(f"*アップロード日時:* {image.uploaded_at}\n\n")

        return "".join(lines)

    def export_month(self, records: list[Record], year: int, month: int) -> tuple[bool, str, str]:
        """
        特定月の記録をエクスポート

        Args:
            records: エクスポートする記録のリスト
            year: 年
            month: 月

        Returns:
            (成功フラグ, メッセージ, 出力ファイルパス)
        """
        filename = f"records_{year:04d}_{month:02d}.md"
        output_path = os.path.join(self.export_dir, filename)

        return self.export_records(records, output_path)
