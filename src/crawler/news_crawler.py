import asyncio
import ssl

from datetime import (
    datetime,
    timezone,
    timedelta
)

from urllib.parse import urlparse

import aiohttp
import certifi
import feedparser

from bs4 import BeautifulSoup

from dateutil import parser as date_parser

from src.models.news import (
    NewsArticle,
    NewsContent,
    NewsSource
)


# ==========================================
# AI NEWS SOURCES
# ==========================================

NEWS_SOURCES = [

    {
        "name": "MIT Technology Review",
        "feed": (
            "https://www.technologyreview.com/"
            "feed/"
        )
    },

    {
        "name": "VentureBeat AI",
        "feed": (
            "https://venturebeat.com/"
            "category/ai/feed/"
        )
    },

    {
        "name": "TechCrunch AI",
        "feed": (
            "https://techcrunch.com/"
            "category/artificial-intelligence/feed/"
        )
    },

    {
        "name": "The Verge AI",
        "feed": (
            "https://www.theverge.com/"
            "rss/index.xml"
        )
    },

    {
        "name": "MarkTechPost",
        "feed": (
            "https://www.marktechpost.com/feed/"
        )
    }
]


# ==========================================
# SETTINGS
# ==========================================

MAX_ARTICLES_PER_SOURCE = 20

CONCURRENCY = 5

FRESHNESS_HOURS = 24


# ==========================================
# DATE PARSING
# ==========================================

def parse_date(value):

    if not value:

        return None

    try:

        parsed_date = date_parser.parse(
            str(value)
        )

        if parsed_date.tzinfo is None:

            parsed_date = parsed_date.replace(
                tzinfo=timezone.utc
            )

        return parsed_date.astimezone(
            timezone.utc
        )

    except Exception:

        return None


def is_fresh(published_date):

    if not published_date:

        return False

    current_time = datetime.now(
        timezone.utc
    )

    time_limit = current_time - timedelta(
        hours=FRESHNESS_HOURS
    )

    return published_date >= time_limit


# ==========================================
# DOWNLOAD ARTICLE HTML
# ==========================================

async def fetch_text(

    session,

    url,

    semaphore

):

    async with semaphore:

        try:

            async with session.get(
                url,

                allow_redirects=True

            ) as response:

                if response.status != 200:

                    return None

                return await response.text(
                    errors="ignore"
                )

        except Exception:

            return None


# ==========================================
# EXTRACT FULL ARTICLE TEXT
# ==========================================

def extract_article_text(html):

    if not html:

        return None

    try:

        soup = BeautifulSoup(

            html,

            "html.parser"

        )


        # Remove unnecessary elements

        for element in soup(

            [

                "script",

                "style",

                "nav",

                "footer",

                "header",

                "aside"

            ]

        ):

            element.decompose()


        # Try article element first

        article = soup.find(
            "article"
        )


        if article:

            paragraphs = article.find_all(
                "p"
            )

        else:

            paragraphs = soup.find_all(
                "p"
            )


        text = " ".join(

            paragraph.get_text(
                " ",
                strip=True
            )

            for paragraph in paragraphs

        )


        # Remove extremely short results

        if len(text) < 200:

            return None


        return text

    except Exception:

        return None


# ==========================================
# PROCESS ONE ARTICLE
# ==========================================

async def process_article(

    entry,

    source,

    session,

    semaphore

):

    try:

        title = getattr(
            entry,

            "title",

            None
        )


        article_url = getattr(
            entry,

            "link",

            None
        )


        if not title or not article_url:

            return None


        # ----------------------------------
        # EXTRACT DATE
        # ----------------------------------

        published_value = (

            getattr(
                entry,

                "published",

                None
            )

            or

            getattr(
                entry,

                "updated",

                None
            )

        )


        published_date = parse_date(
            published_value
        )


        # Strict 24-hour freshness

        if not is_fresh(
            published_date
        ):

            return None


        # ----------------------------------
        # EXTRACT FULL TEXT
        # ----------------------------------

        html = await fetch_text(

            session,

            article_url,

            semaphore

        )


        full_text = extract_article_text(
            html
        )


        # ----------------------------------
        # CREATE RECORD
        # ----------------------------------

        collected_at = datetime.now(
            timezone.utc
        ).isoformat()


        return NewsArticle(

            source=NewsSource(

                name=source["name"],

                url=article_url
            ),

            content=NewsContent(

                title=str(title),

                articleUrl=article_url,

                fullText=full_text,

                publishedAt=published_date.isoformat(),

                author=getattr(
                    entry,

                    "author",

                    None
                )
            ),

            collectedAt=collected_at
        )

    except Exception as error:

        print(
            f"Article processing error: "
            f"{error}"
        )

        return None


# ==========================================
# PROCESS ONE SOURCE
# ==========================================

async def process_source(

    source,

    session,

    semaphore

):

    print(
        f"\nChecking: "
        f"{source['name']}"
    )


    try:

        async with session.get(

            source["feed"]

        ) as response:

            print(
                f"Feed status: "
                f"{response.status}"
            )


            if response.status != 200:

                return []


            feed_text = await response.text(
                errors="ignore"
            )


        feed = feedparser.parse(
            feed_text
        )


        entries = feed.entries[
            :MAX_ARTICLES_PER_SOURCE
        ]


        print(
            f"Feed articles found: "
            f"{len(entries)}"
        )


        tasks = [

            process_article(

                entry,

                source,

                session,

                semaphore

            )

            for entry in entries

        ]


        results = await asyncio.gather(
            *tasks,

            return_exceptions=True
        )


        articles = [

            result

            for result in results

            if isinstance(
                result,

                NewsArticle
            )
        ]


        print(
            f"Fresh articles: "
            f"{len(articles)}"
        )


        return articles


    except Exception as error:

        print(
            f"Source error: "
            f"{error}"
        )

        return []


# ==========================================
# MAIN NEWS COLLECTION
# ==========================================

async def get_news():

    print("\n" + "=" * 60)

    print(
        "AI NEWS DATA COLLECTION"
    )

    print("=" * 60)


    ssl_context = ssl.create_default_context(

        cafile=certifi.where()

    )


    connector = aiohttp.TCPConnector(

        ssl=ssl_context

    )


    timeout = aiohttp.ClientTimeout(

        total=60

    )


    headers = {

        "User-Agent":

        (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/120.0"
        )

    }


    semaphore = asyncio.Semaphore(
        CONCURRENCY
    )


    all_articles = []


    async with aiohttp.ClientSession(

        connector=connector,

        timeout=timeout,

        headers=headers

    ) as session:


        tasks = [

            process_source(

                source,

                session,

                semaphore

            )

            for source in NEWS_SOURCES

        ]


        results = await asyncio.gather(
            *tasks
        )


        for articles in results:

            all_articles.extend(
                articles
            )


    # ======================================
    # REMOVE DUPLICATES
    # ======================================

    unique_articles = []

    seen_urls = set()


    for article in all_articles:

        url = article.content.articleUrl


        if url not in seen_urls:

            seen_urls.add(
                url
            )

            unique_articles.append(
                article
            )


    print("\n" + "=" * 60)

    print(
        f"TOTAL FRESH NEWS: "
        f"{len(unique_articles)}"
    )

    print("=" * 60)


    return unique_articles