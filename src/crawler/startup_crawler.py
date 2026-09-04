import ssl
from datetime import datetime, timezone

import aiohttp
import certifi

from src.models.startup import (
    Source,
    Startup,
    StartupContent
)


STARTUP_SOURCES = [

    # Primary CDN
    "https://cdn.jsdelivr.net/gh/"
    "yigitmeteozcan/startups@main/"
    "data/all.json",

    # GitHub raw file fallback
    "https://raw.githubusercontent.com/"
    "yigitmeteozcan/startups/"
    "main/data/all.json"
]


async def fetch_startup_data():

    ssl_context = ssl.create_default_context(
        cafile=certifi.where()
    )

    connector = aiohttp.TCPConnector(
        ssl=ssl_context
    )

    timeout = aiohttp.ClientTimeout(
        total=120
    )

    headers = {
        "User-Agent":
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AI-Data-Intelligence-Pipeline/1.0",

        "Accept":
        "application/json,text/plain,*/*"
    }

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers=headers
    ) as session:

        for url in STARTUP_SOURCES:

            try:

                print(
                    f"\nTrying startup source:\n{url}"
                )

                async with session.get(
                    url,
                    allow_redirects=True
                ) as response:

                    if response.status != 200:

                        print(
                            f"Source failed with "
                            f"status: {response.status}"
                        )

                        continue

                    data = await response.json(
                        content_type=None
                    )

                    if isinstance(data, list):

                        print(
                            f"Successfully downloaded "
                            f"{len(data)} records"
                        )

                        return data

                    print(
                        "Invalid data format received"
                    )

            except Exception as error:

                print(
                    f"Source error: {error}"
                )

    return []


def parse_startups(
    raw_data,
    total_startups=1000
):

    startups = []

    seen_names = set()

    collected_at = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    for item in raw_data:

        if len(startups) >= total_startups:
            break

        try:

            name = item.get("name")

            if not name:
                continue

            normalized_name = (
                name
                .strip()
                .lower()
            )

            if normalized_name in seen_names:
                continue

            seen_names.add(
                normalized_name
            )

            website = item.get(
                "website"
            )

            description = item.get(
                "description"
            )

            location = item.get(
                "location"
            )

            tags = item.get(
                "tags",
                []
            )

            industry = None

            if tags:

                if isinstance(tags, list):

                    industry = ", ".join(
                        str(tag)
                        for tag in tags[:5]
                    )

                else:

                    industry = str(tags)

            source_name = item.get(
                "source",
                "Startup Portfolios API"
            )

            # Dataset URL is retained as
            # a legitimate traceable source.
            source_url = (
                "https://github.com/"
                "yigitmeteozcan/startups"
            )

            startup = Startup(

                source=Source(

                    name=str(
                        source_name
                    ),

                    url=source_url
                ),

                content=StartupContent(

                    entityName=name,

                    employeeCount=None,

                    website=website,

                    description=description,

                    industry=industry,

                    location=location
                ),

                collectedAt=collected_at
            )

            startups.append(
                startup
            )

        except Exception as error:

            print(
                f"Skipping startup: {error}"
            )

    return startups


async def get_startups(
    total_startups=1000
):

    print("\n" + "=" * 60)

    print(
        "STARTUP DATA COLLECTION"
    )

    print("=" * 60)

    raw_data = await fetch_startup_data()

    if not raw_data:

        print(
            "\nAll startup sources failed."
        )

        return []

    startups = parse_startups(
        raw_data,
        total_startups
    )

    print(
        f"\nUnique startups collected: "
        f"{len(startups)}"
    )

    return startups