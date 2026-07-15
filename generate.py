from pathlib import Path
from urllib.parse import urljoin
from xml.sax.saxutils import escape

import requests
from bs4 import BeautifulSoup


URL = "https://chiikawa-info.jp/"
OUTPUT_FILE = Path("chiikawa.xml")


def main() -> None:
    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0",
        },
        timeout=20,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # ちいかわインフォ内の個別コンテンツ候補を探す
    for link in soup.find_all("a", href=True):
        href = link["href"].strip()

        if not href.startswith("/p"):
            continue

        title = link.get_text(" ", strip=True)

        if not title:
            image = link.find("img")

            if image:
                title = image.get("alt", "").strip()

        if not title:
            continue

        article_url = urljoin(URL, href)

        rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>ちいかわ最新情報</title>
<link>{URL}</link>
<description>ちいかわインフォの最新情報1件</description>
<item>
<title>{escape(title)}</title>
<link>{escape(article_url)}</link>
<guid>{escape(article_url)}</guid>
</item>
</channel>
</rss>
"""

        OUTPUT_FILE.write_text(rss, encoding="utf-8")

        print(f"タイトル: {title}")
        print(f"URL: {article_url}")
        print(f"生成完了: {OUTPUT_FILE}")

        return

    raise RuntimeError("ちいかわ最新情報を取得できませんでした")


if __name__ == "__main__":
    main()