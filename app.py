
from flask import Flask, render_template
import requests
import feedparser
import html
import re

app = Flask(__name__)

COUNTRIES = {
    "world": "World",
    "bd": "Bangladesh",
    "in": "India",
    "gb": "United Kingdom",
    "us": "USA",
    "ca": "Canada",
    "au": "Australia"
}

SOURCES = {
    "world": [
        {
            "name": "BBC News",
            "url": "https://feeds.bbci.co.uk/news/world/rss.xml"
        },
        {
            "name": "Al Jazeera",
            "url": "https://www.aljazeera.com/xml/rss/all.xml"
        },
        {
            "name": "The Guardian",
            "url": "https://www.theguardian.com/world/rss"
        }
    ],
    "bd": [
        {
            "name": "Google News Bangladesh",
            "url": "https://news.google.com/rss/search?q=Bangladesh&hl=en-US&gl=US&ceid=US:en"
        }
    ],
    "in": [
        {
            "name": "Google News India",
            "url": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        }
    ],
    "gb": [
        {
            "name": "Google News UK",
            "url": "https://news.google.com/rss?hl=en-GB&gl=GB&ceid=GB:en"
        }
    ],
    "us": [
        {
            "name": "Google News USA",
            "url": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        }
    ],
    "ca": [
        {
            "name": "Google News Canada",
            "url": "https://news.google.com/rss?hl=en-CA&gl=CA&ceid=CA:en"
        }
    ],
    "au": [
        {
            "name": "Google News Australia",
            "url": "https://news.google.com/rss?hl=en-AU&gl=AU&ceid=AU:en"
        }
    ]
}


def clean_text(text):
    text = re.sub(r"<[^>]*>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def get_image(entry):
    # RSS media:content
    for item in entry.get("media_content", []):
        url = item.get("url", "")
        if url and url.startswith(("https://", "http://")):
            return url

    # RSS media:thumbnail
    for item in entry.get("media_thumbnail", []):
        url = item.get("url", "")
        if url and url.startswith(("https://", "http://")):
            return url

    # RSS enclosure
    for item in entry.get("enclosures", []):
        url = item.get("href") or item.get("url", "")
        if url and url.startswith(("https://", "http://")):
            return url

    # Image embedded in the description
    description = entry.get("description", "")
    match = re.search(
        r'<img[^>]+src=["\']([^"\']+)["\']',
        description,
        re.IGNORECASE
    )

    if match:
        url = html.unescape(match.group(1))
        if url.startswith(("https://", "http://")):
            return url

    # Google News RSS sometimes contains thumbnails in summary HTML
    summary = entry.get("summary", "")
    match = re.search(
        r'<img[^>]+src=["\']([^"\']+)["\']',
        summary,
        re.IGNORECASE
    )

    if match:
        url = html.unescape(match.group(1))
        if url.startswith(("https://", "http://")):
            return url

    return ""


def get_news(country="world"):
    articles = []
    seen_links = set()

    for source in SOURCES.get(country, SOURCES["world"]):
        try:
            response = requests.get(
                source["url"],
                headers={
                    "User-Agent": "Mozilla/5.0 WorldPulseNews/1.0"
                },
                timeout=15
            )
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if feed.bozo and not feed.entries:
                print(f'Could not parse feed: {source["name"]}')
                continue

            for entry in feed.entries[:20]:
                link = entry.get("link", "")

                if not link or link in seen_links:
                    continue

                seen_links.add(link)

                description = (
                    entry.get("summary")
                    or entry.get("description")
                    or ""
                )

                articles.append({
                    "title": clean_text(
                        entry.get("title", "Untitled News")
                    ),
                    "description": clean_text(description)
                    or "Open the article to read the full story.",
                    "image": get_image(entry),
                    "url": link,
                    "source": source["name"],
                    "published": entry.get("published", "")
                })

        except Exception as error:
            print(f'{source["name"]} error: {error}')

    return articles


@app.route("/")
def home():
    return show_news("world")


@app.route("/country/<country_code>")
def country_news(country_code):
    if country_code not in COUNTRIES:
        country_code = "world"

    return show_news(country_code)


def show_news(country_code):
    news = get_news(country_code)

    return render_template(
        "index.html",
        news=news,
        countries=COUNTRIES,
        selected_country=country_code,
        country_name=COUNTRIES[country_code]
    )


if __name__ == "__main__":
    app.run(debug=True)
