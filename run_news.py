import asyncio

from src.crawler.news_crawler import (
    get_news
)

from src.storage.news_storage import (
    save_news
)


async def main():

    articles = await get_news()

    save_news(
        articles
    )

    print(

        f"\nFINAL NEWS COUNT: "
        f"{len(articles)}"

    )


if __name__ == "__main__":

    asyncio.run(main())