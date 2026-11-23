#!/usr/bin/env python3
"""app/icons/icon.svg から PNG のアイコンを作る（Playwright が必要なので、コンテナで実行する）。

    ./dev py tools/make_icons.py

アイコンの SVG を変えたときだけ実行し、できた PNG をコミットする。
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "app" / "icons"
SVG = (ICONS / "icon.svg").read_text(encoding="utf-8")

# (ファイル名, 一辺のピクセル, 絵柄の大きさ（割合）, 背景を全面に塗るか)
# - 通常のアイコンは角が透明
# - iPhone のホーム画面用（apple-touch-icon）は、透明な角が黒くなるので背景を全面に塗る
# - maskable は端末側で丸く切り抜かれるので、背景を全面に塗り、絵柄を中央80%に収める
TARGETS = [
    ("icon-192.png", 192, 1.0, False),
    ("icon-512.png", 512, 1.0, False),
    ("apple-touch-icon.png", 180, 1.0, True),
    ("icon-maskable-512.png", 512, 0.8, True),
]


def page_html(size: int, scale: float, opaque: bool) -> str:
    inner = int(size * scale)
    bg = "#0f766e" if opaque else "transparent"
    body = f'<div style="width:{size}px;height:{size}px;background:{bg};display:grid;place-items:center">' \
           f'<div style="width:{inner}px;height:{inner}px">{SVG}</div></div>'
    return f"<html><body style='margin:0;background:transparent'>{body}</body></html>"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, size, scale, opaque in TARGETS:
            page = browser.new_page(viewport={"width": size, "height": size})
            page.set_content(page_html(size, scale, opaque))
            page.locator("svg").first.evaluate("(s) => { s.setAttribute('width', '100%'); s.setAttribute('height', '100%'); }")
            page.screenshot(path=str(ICONS / name), omit_background=not opaque)
            page.close()
            print(f"  {name}（{size}px）")
        browser.close()


if __name__ == "__main__":
    main()
