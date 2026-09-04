from dotenv import load_dotenv

import asyncio


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# RESEARCH PAPER IMPORTS
# ==========================================

from src.crawler.arxiv_crawler import (
    get_research_papers
)

from src.services.paper_enrichment import (
    enrich_papers_with_github
)

from src.storage.file_storage import (
    save_papers
)


# ==========================================
# STARTUP IMPORTS
# ==========================================

from src.crawler.startup_crawler import (
    get_startups
)

from src.storage.startup_storage import (
    save_startups
)


# ==========================================
# PRODUCT IMPORTS
# ==========================================

from src.crawler.product_crawler import (
    get_products
)

from src.storage.product_storage import (
    save_products
)


# ==========================================
# MAIN PIPELINE
# ==========================================

async def main():

    print("\n" + "=" * 60)

    print(
        "AI DATA INTELLIGENCE PIPELINE"
    )

    print("=" * 60)


    # ======================================
    # STEP 1: COLLECT RESEARCH PAPERS
    # ======================================

    print(
        "\n[1/7] Collecting research papers..."
    )

    papers = await get_research_papers(

        total_papers=1000,

        batch_size=100
    )


    print(
        f"\nCollected {len(papers)} "
        f"research papers"
    )


    # ======================================
    # STEP 2: GITHUB ENRICHMENT
    # ======================================

    print(
        "\n[2/7] Fetching GitHub metrics..."
    )

    papers = await enrich_papers_with_github(

        papers,

        concurrency=3
    )


    # Papers containing GitHub URLs

    papers_with_github = [

        paper

        for paper in papers

        if paper.github_url
    ]


    # Papers with successfully retrieved
    # GitHub star data

    papers_with_stars = [

        paper

        for paper in papers

        if paper.github_stars is not None
    ]


    print(
        f"\nPapers with GitHub URLs: "
        f"{len(papers_with_github)}"
    )


    print(
        f"Papers with GitHub star data: "
        f"{len(papers_with_stars)}"
    )


    # ======================================
    # STEP 3: SAVE RESEARCH PAPERS
    # ======================================

    print(
        "\n[3/7] Saving research papers..."
    )

    save_papers(papers)


    # ======================================
    # STEP 4: COLLECT STARTUPS
    # ======================================

    print(
        "\n[4/7] Collecting startup data..."
    )

    startups = await get_startups(

        total_startups=1000
    )


    print(
        f"\nCollected {len(startups)} "
        f"startups"
    )


    # ======================================
    # STEP 5: SAVE STARTUPS
    # ======================================

    print(
        "\n[5/7] Saving startup data..."
    )

    save_startups(startups)


    # ======================================
    # STEP 6: COLLECT PRODUCTS
    # ======================================

    print(
        "\n[6/7] Collecting product data..."
    )

    products = await get_products(

        total_products=1000
    )


    print(
        f"\nCollected {len(products)} "
        f"products"
    )


    # ======================================
    # STEP 7: SAVE PRODUCTS
    # ======================================

    print(
        "\n[7/7] Saving product data..."
    )

    save_products(products)


    # ======================================
    # FINAL SUMMARY
    # ======================================

    print("\n" + "=" * 60)

    print(
        "PIPELINE COMPLETED SUCCESSFULLY"
    )

    print("=" * 60)


    print(

        f"\nResearch Papers: "
        f"{len(papers)}"
    )


    print(

        f"Research Papers with "
        f"GitHub URLs: "
        f"{len(papers_with_github)}"
    )


    print(

        f"Research Papers with "
        f"GitHub Star Data: "
        f"{len(papers_with_stars)}"
    )


    print(

        f"\nStartups: "
        f"{len(startups)}"
    )


    print(

        f"Products: "
        f"{len(products)}"
    )


    print("\n" + "=" * 60)

    print(
        "ALL AVAILABLE DATA SAVED SUCCESSFULLY!"
    )

    print("=" * 60 + "\n")


# ==========================================
# PROGRAM ENTRY POINT
# ==========================================

if __name__ == "__main__":

    asyncio.run(main())