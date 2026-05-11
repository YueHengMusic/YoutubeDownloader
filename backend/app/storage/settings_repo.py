from __future__ import annotations

import json
from pathlib import Path


class SettingsRepository:
    """
    用户设置持久化仓库（JSON 文件）。

    设计目标：
    - 结构简单、可读性高，方便桌面端本地排查；
    - 字段缺失或文件损坏时自动回退默认值，保证应用可启动。
    """

    DEFAULT_DOWNLOAD_CONCURRENCY = 2
    MIN_DOWNLOAD_CONCURRENCY = 1
    MAX_DOWNLOAD_CONCURRENCY = 20

    def __init__(self, settings_path: Path) -> None:
        self.settings_path = settings_path

    def get_download_concurrency(self) -> int:
        """读取并发下载数量；若未配置则返回默认值。"""
        raw_settings = self._read_all()
        raw_value = raw_settings.get("download_concurrency")
        return self._normalize_download_concurrency(raw_value)

    def set_download_concurrency(self, value: int) -> int:
        """
        保存并发下载数量，返回最终写入值（已过边界纠正）。
        """
        normalized_value = self._normalize_download_concurrency(value)
        raw_settings = self._read_all()
        raw_settings["download_concurrency"] = normalized_value
        self._write_all(raw_settings)
        return normalized_value

    def _normalize_download_concurrency(self, raw_value: object) -> int:
        """
        并发值标准化：
        - 非数字或非法值回退默认值；
        - 强制限制到 [MIN, MAX]，避免异常配置影响队列行为。
        """
        try:
            parsed_value = int(raw_value)  # type: ignore[arg-type]
        except Exception:
            return self.DEFAULT_DOWNLOAD_CONCURRENCY
        if parsed_value < self.MIN_DOWNLOAD_CONCURRENCY:
            return self.MIN_DOWNLOAD_CONCURRENCY
        if parsed_value > self.MAX_DOWNLOAD_CONCURRENCY:
            return self.MAX_DOWNLOAD_CONCURRENCY
        return parsed_value

    def _read_all(self) -> dict:
        if not self.settings_path.exists():
            return {}
        try:
            raw_text = self.settings_path.read_text(encoding="utf-8")
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                return parsed
            return {}
        except Exception:
            # 配置损坏时回退默认，避免阻塞应用使用。
            return {}

    def _write_all(self, value: dict) -> None:
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
