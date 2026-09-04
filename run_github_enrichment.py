import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.models.research_paper import ResearchPaper
from src.services.paper_enrichment import (
    enrich_papers_with_github
)


INPUT_FILE = Path(
    "data/output/research_papers.json"
)


async def main():

    print("=" * 60)
    print("GITHUB STAR ENRICHMENT")
    print("=" * 60)

    # ---------------------------------
    # LOAD EXISTING PAPERS
    # ---------------------------------

    if not INPUT_FILE.exists():

        print(
            f"ERROR: File not found: "
            f"{INPUT_FILE}"
        )

        return

    print("\nLoading existing research papers...")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    papers = []

    for item in data:

        try:

            paper = ResearchPaper(**item)

            papers.append(paper)

        except Exception as error:

            print(
                f"Skipping invalid paper: "
                f"{error}"
            )

    print(
        f"Loaded {len(papers)} papers"
    )

    # ---------------------------------
    # CHECK GITHUB URLS
    # ---------------------------------

    papers_with_github = [

        paper

        for paper in papers

        if paper.github_url
    ]

    print(
        f"Papers with GitHub URLs: "
        f"{len(papers_with_github)}"
    )

    # ---------------------------------
    # FETCH STARS
    # ---------------------------------

    print(
        "\nFetching GitHub stars..."
    )

    papers = await enrich_papers_with_github(

        papers,

        concurrency=3
    )

    # ---------------------------------
    # RESULTS
    # ---------------------------------

    papers_with_stars = [

        paper

        for paper in papers

        if paper.github_stars is not None
    ]

    print("\n" + "=" * 60)

    print(
        f"Papers with star data: "
        f"{len(papers_with_stars)}"
    )

    print("=" * 60)

    # ---------------------------------
    # SAVE UPDATED DATA
    # ---------------------------------

    updated_data = [

        paper.model_dump()

        for paper in papers

    ]

    with open(
        INPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            updated_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        "\nUpdated research papers "
        "saved successfully!"
    )


if __name__ == "__main__":

    asyncio.run(main())