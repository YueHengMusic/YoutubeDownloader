from app.core.cookie_manager import CookieManager
from app.models.task import CookieMode


def test_cookie_args_none() -> None:
    # 不使用 Cookie 时，不应拼接任何额外参数。
    assert CookieManager.cookie_args(CookieMode.none, None) == []


def test_cookie_args_browser() -> None:
    # 浏览器模式应正确生成 --cookies-from-browser 参数。
    assert CookieManager.cookie_args(CookieMode.browser, "edge") == [
        "--cookies-from-browser",
        "edge",
    ]
