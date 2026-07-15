from pathlib import Path
from urllib.parse import urljoin
from xml.sax.saxutils import escape

import requests
from bs4 import BeautifulSoup


URL = "https://chiikawapark.com/"

OUTPUT_FILE_1 = Path("chiikawa.xml")
OUTPUT_FILE_2 = Path("chiikawa2.xml")


def create_rss(title: str, article_url: str, description: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>ちいかわ最新情報</title>
<link>{URL}</link>
<description>{escape(description)}</description>
<item>
<title>{escape(title)}</title>
<guid>{escape(article_url)}</guid>
</item>
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

    first_title, first_url = articles[0]
    second_title, second_url = articles[1]

    OUTPUT_FILE_1.write_text(
        create_rss(
            first_title,
            first_url,
            "ちいかわ＠にゅーすの最新1件目",
        ),
        encoding="utf-8",
    )

    OUTPUT_FILE_2.write_text(
        create_rss(
            second_title,
            second_url,
            "ちいかわ＠にゅーすの最新2件目",
        ),
        encoding="utf-8",
    )

    print("最新1件目:")
    print(f"  {first_title}")
    print(f"  {first_url}")

    print()

    print("最新2件目:")
    print(f"  {second_title}")
    print(f"  {second_url}")

    print()
    print(f"生成完了: {OUTPUT_FILE_1}")
    print(f"生成完了: {OUTPUT_FILE_2}")


if __name__ == "__main__":
    main()