from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务生命周期状态。"""
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"


class CookieMode(str, Enum):
    """Cookie 使用策略。"""
    none = "none"
    file = "file"
    browser = "browser"


class DownloadTarget(str, Enum):
    """下载目标类型。"""
    video = "video"
    audio = "audio"
    thumbnail = "thumbnail"


class ResolutionMode(str, Enum):
    """分辨率策略。"""
    prefer = "prefer"
    limit = "limit"


class SubtitleMode(str, Enum):
    """字幕下载策略。"""
    none = "none"
    manual = "manual"
    auto = "auto"
    all = "all"


class CreateTaskRequest(BaseModel):
    """创建任务接口的请求体。"""
    url: str = Field(min_length=1)
    output_dir: str = Field(min_length=1)
    download_target: DownloadTarget = DownloadTarget.video
    format_id: Optional[str] = None
    resolution: Optional[str] = None
    resolution_mode: ResolutionMode = ResolutionMode.prefer
    audio_format: Optional[str] = None
    subtitle_mode: SubtitleMode = SubtitleMode.none
    subtitle_langs: Optional[str] = None
    write_info_json: bool = False
    write_description: bool = False
    write_thumbnail: bool = False
    embed_thumbnail: bool = False
    cookie_mode: CookieMode = CookieMode.none
    cookie_value: Optional[str] = None


class DownloadTask(BaseModel):
    """单个任务的运行态 + 持久化快照结构。"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    url: str
    output_dir: str
    download_target: DownloadTarget = DownloadTarget.video
    format_id: Optional[str] = None
    resolution: Optional[str] = None
    resolution_mode: ResolutionMode = ResolutionMode.prefer
    audio_format: Optional[str] = None
    subtitle_mode: SubtitleMode = SubtitleMode.none
    subtitle_langs: Optional[str] = None
    write_info_json: bool = False
    write_description: bool = False
    write_thumbnail: bool = False
    embed_thumbnail: bool = False
    cookie_mode: CookieMode = CookieMode.none
    cookie_value: Optional[str] = None
    status: TaskStatus = TaskStatus.pending
    progress: float = 0.0
    speed: Optional[str] = None
    eta: Optional[str] = None
    log: str = ""
    error: Optional[str] = None
    result_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskActionResponse(BaseModel):
    """任务动作接口的统一返回模型。"""
    ok: bool
    message: str
