"""データ永続化・ストレージ管理"""
import json
import os
import shutil
from typing import Dict, Optional, List
from datetime import datetime
from .record import Record


class Storage:
    """JSON形式でのデータ保存・読み込みを管理"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.records_file = os.path.join(data_dir, "records.json")
        self.backup_file = self.records_file + ".bak"
        self._ensure_data_structure()

    def _ensure_data_structure(self):
        """データディレクトリとファイルの存在を確認・初期化"""
        os.makedirs(self.data_dir, exist_ok=True)

        if not os.path.exists(self.records_file):
            self._write_data({
                "version": "1.0",
                "records": {},
                "metadata": {
                    "total_records": 0,
                    "first_record_date": None,
                    "last_updated": datetime.now().isoformat()
                }
            })

    def _read_data(self) -> dict:
        """JSONファイルからデータを読み込み"""
        try:
            with open(self.records_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"データ読み込みエラー: {e}")
            # バックアップから復元を試みる
            if os.path.exists(self.backup_file):
                print("バックアップから復元を試みます...")
                try:
                    with open(self.backup_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as backup_error:
                    print(f"バックアップ復元失敗: {backup_error}")

            # 初期化データを返す
            return {
                "version": "1.0",
                "records": {},
                "metadata": {
                    "total_records": 0,
                    "first_record_date": None,
                    "last_updated": datetime.now().isoformat()
                }
            }

    def _write_data(self, data: dict):
        """データをJSONファイルに書き込み（バックアップ作成）"""
        # 既存ファイルをバックアップ
        if os.path.exists(self.records_file):
            try:
                shutil.copy2(self.records_file, self.backup_file)
            except Exception as e:
                print(f"バックアップ作成警告: {e}")

        # データを書き込み
        try:
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"データ書き込みエラー: {e}")
            # バックアップから復元
            if os.path.exists(self.backup_file):
                shutil.copy2(self.backup_file, self.records_file)
            raise

    def _update_metadata(self, data: dict):
        """メタデータを更新"""
        records = data.get("records", {})
        data["metadata"] = {
            "total_records": len(records),
            "first_record_date": min(records.keys()) if records else None,
            "last_updated": datetime.now().isoformat()
        }

    def get_record(self, date: str) -> Optional[Record]:
        """指定日の記録を取得"""
        data = self._read_data()
        record_data = data.get("records", {}).get(date)
        if record_data:
            return Record.from_dict(record_data)
        return None

    def get_all_records(self) -> Dict[str, Record]:
        """全ての記録を取得"""
        data = self._read_data()
        records = {}
        for date, record_data in data.get("records", {}).items():
            records[date] = Record.from_dict(record_data)
        return records

    def get_records_by_month(self, year: int, month: int) -> Dict[str, Record]:
        """指定月の記録を取得"""
        data = self._read_data()
        records = {}
        month_prefix = f"{year:04d}-{month:02d}"

        for date, record_data in data.get("records", {}).items():
            if date.startswith(month_prefix):
                records[date] = Record.from_dict(record_data)
        return records

    def get_dates_with_records(self) -> List[str]:
        """記録が存在する日付のリストを取得"""
        data = self._read_data()
        return list(data.get("records", {}).keys())

    def save_record(self, record: Record):
        """記録を保存（新規作成または更新）"""
        data = self._read_data()
        data["records"][record.date] = record.to_dict()
        self._update_metadata(data)
        self._write_data(data)

    def delete_record(self, date: str) -> bool:
        """記録を削除"""
        data = self._read_data()
        if date in data.get("records", {}):
            del data["records"][date]
            self._update_metadata(data)
            self._write_data(data)
            return True
        return False

    def record_exists(self, date: str) -> bool:
        """指定日に記録が存在するか確認"""
        data = self._read_data()
        return date in data.get("records", {})

    def get_metadata(self) -> dict:
        """メタデータを取得"""
        data = self._read_data()
        return data.get("metadata", {})
