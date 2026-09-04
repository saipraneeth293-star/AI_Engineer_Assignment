import json

from pathlib import Path


OUTPUT_FILE = Path(
    "data/output/news.json"
)


def save_news(news_articles):

    OUTPUT_FILE.parent.mkdir(

        parents=True,

        exist_ok=True

    )


    data = [

        article.model_dump()

        for article in news_articles

    ]


    with open(

        OUTPUT_FILE,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            data,

            file,

            indent=4,

            ensure_ascii=False

        )


    print(

        f"Saved "
        f"{len(news_articles)} "
        f"news records"

    )