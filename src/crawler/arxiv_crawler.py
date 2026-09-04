import asyncio
import ssl
import xml.etree.ElementTree as ET

import aiohttp
import certifi

from src.models.research_paper import ResearchPaper
from src.services.github_service import extract_github_urls


# arXiv API URL
ARXIV_API = "https://export.arxiv.org/api/query"


async def fetch_arxiv_batch(
    session,
    start: int,
    batch_size: int = 100
):
    """
    Fetch a batch of AI/ML research papers from arXiv.
    """

    params = {
        "search_query": "cat:cs.AI OR cat:cs.LG",
        "start": start,
        "max_results": batch_size,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    max_retries = 3

    for attempt in range(max_retries):

        try:

            async with session.get(
                ARXIV_API,
                params=params
            ) as response:

                response.raise_for_status()

                return await response.text()

        except Exception as error:

            print(
                f"Error fetching batch "
                f"{start}-{start + batch_size}"
            )

            print(
                f"Attempt {attempt + 1}/{max_retries}: "
                f"{error}"
            )

            if attempt < max_retries - 1:

                wait_time = 2 ** attempt

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                await asyncio.sleep(wait_time)

            else:

                print(
                    f"Failed batch starting at {start}"
                )

                return None


def parse_arxiv_response(xml_data: str):
    """
    Parse XML returned by the arXiv API.
    """

    if not xml_data:
        return []

    try:

        root = ET.fromstring(xml_data)

    except ET.ParseError as error:

        print(
            f"XML parsing error: {error}"
        )

        return []

    namespace = {
        "atom": "http://www.w3.org/2005/Atom"
    }

    papers = []

    entries = root.findall(
        "atom:entry",
        namespace
    )

    print(
        f"Papers found in batch: "
        f"{len(entries)}"
    )

    for entry in entries:

        try:

            # ---------------------------
            # TITLE
            # ---------------------------

            title_element = entry.find(
                "atom:title",
                namespace
            )

            if title_element is None:

                continue

            title = (
                title_element.text
                .strip()
                .replace("\n", " ")
            )

            title = " ".join(
                title.split()
            )


            # ---------------------------
            # PAPER URL
            # ---------------------------

            url_element = entry.find(
                "atom:id",
                namespace
            )

            if url_element is None:

                continue

            paper_url = (
                url_element.text.strip()
            )


            # ---------------------------
            # PUBLICATION DATE
            # ---------------------------

            published_element = entry.find(
                "atom:published",
                namespace
            )

            if published_element is None:

                continue

            published_date = (
                published_element.text.strip()
            )


            # ---------------------------
            # AUTHORS
            # ---------------------------

            authors = []

            author_elements = entry.findall(
                "atom:author",
                namespace
            )

            for author in author_elements:

                name_element = author.find(
                    "atom:name",
                    namespace
                )

                if (
                    name_element is not None
                    and name_element.text
                ):

                    authors.append(
                        name_element.text.strip()
                    )


            # ---------------------------
            # ABSTRACT / SUMMARY
            # ---------------------------

            summary_element = entry.find(
                "atom:summary",
                namespace
            )

            summary = ""

            if (
                summary_element is not None
                and summary_element.text
            ):

                summary = (
                    summary_element.text
                    .strip()
                    .replace("\n", " ")
                )

                summary = " ".join(
                    summary.split()
                )


            # ---------------------------
            # GITHUB URL DETECTION
            # ---------------------------

            github_urls = extract_github_urls(
                summary
            )

            github_url = None

            if github_urls:

                github_url = github_urls[0]


            # ---------------------------
            # CREATE RESEARCH PAPER
            # ---------------------------

            paper = ResearchPaper(

                title=title,

                authors=authors,

                paper_url=paper_url,

                github_url=github_url,

                github_stars=None,

                published_date=published_date
            )

            papers.append(paper)


        except Exception as error:

            print(
                f"Error parsing paper: "
                f"{error}"
            )

            continue


    return papers


async def get_research_papers(
    total_papers: int = 1000,
    batch_size: int = 100
):
    """
    Fetch the requested number of research papers.

    Example:

    total_papers = 1000
    batch_size = 100

    This makes approximately 10 requests.
    """

    all_papers = []


    # ---------------------------
    # SSL CONFIGURATION
    # ---------------------------

    ssl_context = ssl.create_default_context(
        cafile=certifi.where()
    )


    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        limit=10
    )


    timeout = aiohttp.ClientTimeout(
        total=60
    )


    headers = {

        "User-Agent":
        "AI-Data-Intelligence-Pipeline/1.0 "
        "(Research Project)"
    }


    # ---------------------------
    # CREATE SESSION
    # ---------------------------

    async with aiohttp.ClientSession(

        connector=connector,

        timeout=timeout,

        headers=headers

    ) as session:


        # ---------------------------
        # FETCH BATCHES
        # ---------------------------

        for start in range(
            0,
            total_papers,
            batch_size
        ):

            end = min(
                start + batch_size,
                total_papers
            )

            print("\n" + "=" * 50)

            print(
                f"Fetching papers "
                f"{start + 1} to {end}"
            )

            print("=" * 50)


            xml_data = await fetch_arxiv_batch(

                session=session,

                start=start,

                batch_size=batch_size
            )


            if not xml_data:

                print(
                    "Skipping failed batch..."
                )

                continue


            papers = parse_arxiv_response(
                xml_data
            )


            # ---------------------------
            # REMOVE DUPLICATES
            # ---------------------------

            existing_urls = {

                paper.paper_url

                for paper in all_papers

            }


            new_papers = [

                paper

                for paper in papers

                if paper.paper_url
                not in existing_urls

            ]


            all_papers.extend(
                new_papers
            )


            print(

                f"New papers collected: "

                f"{len(new_papers)}"

            )


            print(

                f"Total unique papers: "

                f"{len(all_papers)}"

            )


            # ---------------------------
            # RESPECT ARXIV API
            # ---------------------------

            if end < total_papers:

                print(
                    "Waiting before next batch..."
                )

                await asyncio.sleep(3)


    # ---------------------------
    # FINAL RESULT
    # ---------------------------

    print("\n" + "=" * 50)

    print(
        f"FINAL PAPER COUNT: "
        f"{len(all_papers)}"
    )

    print("=" * 50)


    return all_papers[:total_papers]