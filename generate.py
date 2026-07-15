from pathlib import Path
from urllib.parse import urljoin
from xml.sax.saxutils import escape

import requests
from bs4 import BeautifulSoup


URL = "https://chiikawapark.com/"

OUTPUT_FILE_1 = Path("chiikawa.xml")
OUTPUT_FILE_2 = Path("chiikawa2.xml")


def create_rss(items: list[tuple[str, str]], description: str) -> str:
    rss_items = ""

    for title, article_url in items:
        rss_items += f"""
<item>
<title>{escape(title)}</title>
<link>{escape(article_url)}</link>
<guid>{escape(article_url)}</guid>
</item>
"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>ちいかわ最新情報</title>
<link>{URL}</link>
<description>{escape(description)}</description>
{rss_items}
</channel>
</rss>
"""


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

    latest_heading = soup.find(
        lambda tag: (
            tag.name in ["h2", "h3"]
            and "最新記事" in tag.get_text()
        )
    )

    if latest_heading is None:
        raise RuntimeError("「最新記事」セクションが見つかりませんでした")

    articles: list[tuple[str, str]] = []
    seen_urls: set[str] = set()

    for article in latest_heading.find_all_next("a", href=True):
        title = article.get_text(" ", strip=True)
        article_url = urljoin(URL, article["href"])

        if not title:
            continue

        if article_url in seen_urls:
            continue

        seen_urls.add(article_url)
        articles.append((title, article_url))

        if len(articles) >= 2:
            break

    if len(articles) < 2:
        raise RuntimeError("最新記事を2件取得できませんでした")

    # 最新1件
    rss_1 = create_rss(
        articles[:1],
        "ちいかわ＠にゅーすの最新記事1件",
    )

    OUTPUT_FILE_1.write_text(
        rss_1,
        encoding="utf-8",
    )

    # 最新2件
    rss_2 = create_rss(
        articles[:2],
        "ちいかわ＠にゅーすの最新記事2件",
    )

    OUTPUT_FILE_2.write_text(
        rss_2,
        encoding="utf-8",
    )

    print("最新1件:")
    print(f"  {articles[0][0]}")
    print(f"  {articles[0][1]}")

    print()

    print("最新2件:")
    for index, (title, article_url) in enumerate(articles[:2], start=1):
        print(f"{index}. {title}")
        print(f"   {article_url}")

    print()
    print(f"生成完了: {OUTPUT_FILE_1}")
    print(f"生成完了: {OUTPUT_FILE_2}")


if __name__ == "__main__":
    main()