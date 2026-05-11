from __future__ import annotations

from pathlib import Path

from app.models.task import CookieMode


class CookieManager:
    @staticmethod
    def validate_cookie_file(path: str) -> None:
        """校验 cookies.txt 路径是否合法。"""
        cookie_file = Path(path)
        if not cookie_file.exists() or not cookie_file.is_file():
            raise ValueError("cookies.txt 文件不存在")
        if cookie_file.suffix.lower() != ".txt":
            raise ValueError("cookies 文件必须是 .txt")

    @staticmethod
    def cookie_args(mode: CookieMode, value: str | None) -> list[str]:
        """根据用户选择拼接 yt-dlp 的 Cookie 参数。"""
        if mode == CookieMode.none:
            return []
        if not value:
            raise ValueError("Cookie 模式需要提供值")
        if mode == CookieMode.file:
            CookieManager.validate_cookie_file(value)
            return ["--cookies", value]
        if mode == CookieMode.browser:
            return ["--cookies-from-browser", value]
        return []
