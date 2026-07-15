from pathlib import Path
from urllib.parse import urljoin
from xml.sax.saxutils import escape

import requests
from bs4 import BeautifulSoup


URL = "https://chiikawapark.com/"
OUTPUT_FILE = Path("chiikawa.xml")


def main() -> None:
    response = requests.get(
        URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/150.0.0.0 Safari/537.36"
            )
        },
        timeout=20,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # 「最新記事」見出しを探す
    latest_heading = soup.find(
        lambda tag: tag.name in ["h2", "h3"] and "最新記事" in tag.get_text()
    )

    if latest_heading is None:
        raise RuntimeError("「最新記事」セクションが見つかりませんでした")

    # 見出しより後にある最初の記事リンクを取得
    article = latest_heading.find_next("a", href=True)

    if article is None:
        raise RuntimeError("最新記事が見つかりませんでした")

    title = article.get_text(" ", strip=True)
    article_url = urljoin(URL, article["href"])

    if not title:
        raise RuntimeError("記事タイトルを取得できませんでした")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>ちいかわ最新情報</title>
<link>{URL}</link>
<description>ちいかわ＠にゅーすの最新記事1件</description>
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


if __name__ == "__main__":
    main()