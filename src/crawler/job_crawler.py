import asyncio
import ssl

from datetime import (
    datetime,
    timezone,
    timedelta
)

import aiohttp
import certifi

from dateutil import parser as date_parser

from src.models.job import (
    Job,
    JobSource,
    JobContent
)


# ==========================================
# FIVE AI COMPANY JOB BOARDS
# ==========================================

JOB_SOURCES = [

    {
        "name": "OpenAI Careers",

        "board": "openai"
    },

    {
        "name": "Anthropic Careers",

        "board": "anthropic"
    },

    {
        "name": "Hugging Face Careers",

        "board": "huggingface"
    },

    {
        "name": "Scale AI Careers",

        "board": "scaleai"
    },

    {
        "name": "Cohere Careers",

        "board": "cohere"
    }
]


FRESHNESS_HOURS = 24

CONCURRENCY = 5


# ==========================================
# DATE UTILITIES
# ==========================================

def parse_date(value):

    if not value:

        return None

    try:

        parsed = date_parser.parse(
            str(value)
        )

        if parsed.tzinfo is None:

            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(
            timezone.utc
        )

    except Exception:

        return None


def is_fresh(date):

    if not date:

        return False

    limit = (

        datetime.now(
            timezone.utc
        )

        -

        timedelta(
            hours=FRESHNESS_HOURS
        )
    )

    return date >= limit


# ==========================================
# ROLE CLASSIFICATION
# ==========================================

def classify_role(title):

    title = title.lower()

    if any(

        word in title

        for word in [

            "engineer",

            "developer",

            "scientist",

            "machine learning",

            "research"
        ]

    ):

        return "Engineering"


    if any(

        word in title

        for word in [

            "product",

            "designer"
        ]

    ):

        return "Product"


    if any(

        word in title

        for word in [

            "sales",

            "business",

            "marketing"
        ]

    ):

        return "Business"


    if any(

        word in title

        for word in [

            "legal",

            "finance",

            "operations"
        ]

    ):

        return "Operations"


    return "Other"


# ==========================================
# FETCH ONE JOB SOURCE
# ==========================================

async def fetch_source(

    source,

    session,

    semaphore

):

    async with semaphore:

        board = source["board"]

        url = (

            "https://boards-api.greenhouse.io/"
            "v1/boards/"
            f"{board}/jobs"
            "?content=true"
        )


        print(

            f"\nChecking: "
            f"{source['name']}"

        )


        try:

            async with session.get(

                url

            ) as response:


                print(

                    f"Status: "
                    f"{response.status}"

                )


                if response.status != 200:

                    return []


                data = await response.json()


        except Exception as error:

            print(

                f"Source error: "
                f"{error}"

            )

            return []


        jobs = []


        for item in data.get(

            "jobs",

            []

        ):


            # ------------------------------
            # DATE
            # ------------------------------

            created_at = parse_date(

                item.get(
                    "updated_at"
                )

                or

                item.get(
                    "created_at"
                )
            )


            # Strict 24-hour rule

            if not is_fresh(
                created_at
            ):

                continue


            # ------------------------------
            # TITLE
            # ------------------------------

            title = item.get(
                "title"
            )


            if not title:

                continue


            # ------------------------------
            # LOCATION
            # ------------------------------

            location_data = item.get(

                "location",

                {}
            )


            location = location_data.get(

                "name",

                None

            )


            # ------------------------------
            # REMOTE DETECTION
            # ------------------------------

            description = item.get(

                "content",

                ""

            )


            remote_text = (

                f"{title} "
                f"{location or ''} "
                f"{description}"

            ).lower()


            is_remote = (

                "remote" in remote_text

            )


            # ------------------------------
            # JOB URL
            # ------------------------------

            job_url = item.get(

                "absolute_url"

            )


            if not job_url:

                continue


            # ------------------------------
            # CREATE RECORD
            # ------------------------------

            job = Job(

                source=JobSource(

                    name=source["name"],

                    url=job_url
                ),

                content=JobContent(

                    title=title,

                    company=source[
                        "name"
                    ].replace(
                        " Careers",
                        ""
                    ),

                    jobUrl=job_url,

                    date=created_at.isoformat(),

                    is_remote=is_remote,

                    role_family=classify_role(
                        title
                    ),

                    location=location,

                    description=description
                ),

                collectedAt=(

                    datetime.now(
                        timezone.utc
                    ).isoformat()

                )
            )


            jobs.append(
                job
            )


        print(

            f"Fresh jobs: "
            f"{len(jobs)}"

        )


        return jobs


# ==========================================
# MAIN COLLECTION
# ==========================================

async def get_jobs():

    print("\n" + "=" * 60)

    print(
        "AI JOB DATA COLLECTION"
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

        "AI-Data-Intelligence-Pipeline/1.0"

    }


    semaphore = asyncio.Semaphore(

        CONCURRENCY

    )


    async with aiohttp.ClientSession(

        connector=connector,

        timeout=timeout,

        headers=headers

    ) as session:


        tasks = [

            fetch_source(

                source,

                session,

                semaphore

            )

            for source in JOB_SOURCES

        ]


        results = await asyncio.gather(

            *tasks,

            return_exceptions=True

        )


    all_jobs = []


    for result in results:

        if isinstance(

            result,

            list

        ):

            all_jobs.extend(
                result
            )


    # ======================================
    # REMOVE DUPLICATES
    # ======================================

    unique_jobs = []

    seen_urls = set()


    for job in all_jobs:

        job_url = job.content.jobUrl


        if job_url not in seen_urls:

            seen_urls.add(
                job_url
            )

            unique_jobs.append(
                job
            )


    print("\n" + "=" * 60)

    print(

        f"TOTAL FRESH JOBS: "
        f"{len(unique_jobs)}"

    )

    print("=" * 60)


    return unique_jobs