import asyncio

from src.services.github_service import (
    create_github_session,
    get_github_stars
)


async def enrich_papers_with_github(
    papers,
    concurrency: int = 3
):

    papers_with_github = [
        paper
        for paper in papers
        if paper.github_url
    ]

    print(
        f"Found {len(papers_with_github)} "
        f"papers with GitHub repositories"
    )

    semaphore = asyncio.Semaphore(concurrency)

    async with await create_github_session() as session:

        async def enrich(paper):

            async with semaphore:

                try:

                    stars = await get_github_stars(
                        session=session,
                        github_url=paper.github_url
                    )

                    paper.github_stars = stars

                    if stars is not None:

                        print(
                            f"Stars: {stars} | "
                            f"{paper.title[:50]}"
                        )

                except Exception as error:

                    print(
                        f"Failed: {paper.title[:40]} "
                        f"| {error}"
                    )

                return paper

        tasks = [
            enrich(paper)
            for paper in papers_with_github
        ]

        await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

    return papers