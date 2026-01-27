"""データモデル定義"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid


@dataclass
class ImageAttachment:
    """画像添付ファイルのデータモデル"""
    id: str
    filename: str
    path: str
    thumbnail_path: str
    uploaded_at: str
    size_bytes: int
    caption: Optional[str] = None

    @staticmethod
    def create(filename: str, path: str, thumbnail_path: str, size_bytes: int, caption: Optional[str] = None) -> 'ImageAttachment':
        """新規画像添付ファイルを作成"""
        return ImageAttachment(
            id=str(uuid.uuid4()),
            filename=filename,
            path=path,
            thumbnail_path=thumbnail_path,
            uploaded_at=datetime.now().isoformat(),
            size_bytes=size_bytes,
            caption=caption
        )

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'filename': self.filename,
            'path': self.path,
            'thumbnail_path': self.thumbnail_path,
            'uploaded_at': self.uploaded_at,
            'size_bytes': self.size_bytes,
            'caption': self.caption
        }

    @staticmethod
    def from_dict(data: dict) -> 'ImageAttachment':
        """辞書から復元"""
        return ImageAttachment(
            id=data['id'],
            filename=data['filename'],
            path=data['path'],
            thumbnail_path=data['thumbnail_path'],
            uploaded_at=data['uploaded_at'],
            size_bytes=data['size_bytes'],
            caption=data.get('caption')
        )


@dataclass
class Record:
    """記録のデータモデル"""
    id: str
    date: str  # YYYY-MM-DD
    created_at: str
    updated_at: str
    text: str
    images: List[ImageAttachment] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    mood: Optional[str] = None  # good, neutral, bad

    @staticmethod
    def create(date: str, text: str = "", tags: List[str] = None, mood: Optional[str] = None) -> 'Record':
        """新規記録を作成"""
        now = datetime.now().isoformat()
        return Record(
            id=str(uuid.uuid4()),
            date=date,
            created_at=now,
            updated_at=now,
            text=text,
            images=[],
            tags=tags or [],
            mood=mood
        )

    def update(self, text: Optional[str] = None, tags: Optional[List[str]] = None, mood: Optional[str] = None):
        """記録を更新"""
        if text is not None:
            self.text = text
        if tags is not None:
            self.tags = tags
        if mood is not None:
            self.mood = mood
        self.updated_at = datetime.now().isoformat()

    def add_image(self, image: ImageAttachment):
        """画像を追加"""
        self.images.append(image)
        self.updated_at = datetime.now().isoformat()

    def remove_image(self, image_id: str) -> Optional[ImageAttachment]:
        """画像を削除"""
        for i, img in enumerate(self.images):
            if img.id == image_id:
                removed = self.images.pop(i)
                self.updated_at = datetime.now().isoformat()
                return removed
        return None

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'date': self.date,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'text': self.text,
            'images': [img.to_dict() for img in self.images],
            'tags': self.tags,
            'mood': self.mood
        }

    @staticmethod
    def from_dict(data: dict) -> 'Record':
        """辞書から復元"""
        images = [ImageAttachment.from_dict(img) for img in data.get('images', [])]
        return Record(
            id=data['id'],
            date=data['date'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            text=data['text'],
            images=images,
            tags=data.get('tags', []),
            mood=data.get('mood')
        )
