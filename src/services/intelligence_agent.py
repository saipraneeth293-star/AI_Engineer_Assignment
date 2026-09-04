import json

from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

from src.services.llm_service import (
    generate_ai_response
)


# ==========================================
# DATA FILES
# ==========================================

DATA_FILES = {

    "research_papers":
        Path("data/output/research_papers.json"),

    "startups":
        Path("data/output/startups.json"),

    "products":
        Path("data/output/products.json"),

    "news":
        Path("data/output/news.json"),

    "jobs":
        Path("data/output/jobs.json")

}


# ==========================================
# LOAD JSON FILE
# ==========================================

def load_json(file_path):

    if not file_path.exists():

        print(
            f"Warning: File not found: "
            f"{file_path}"
        )

        return []


    try:

        with open(

            file_path,

            "r",

            encoding="utf-8"

        ) as file:

            data = json.load(file)


        if isinstance(data, list):

            return data


        return []

    except Exception as error:

        print(

            f"Error loading "
            f"{file_path}: {error}"

        )

        return []


# ==========================================
# EXTRACT FIELD SAFELY
# ==========================================

def get_nested_value(

    data,

    keys,

    default=None

):

    current = data


    try:

        for key in keys:

            current = current[key]


        return current

    except (

        KeyError,

        TypeError

    ):

        return default


# ==========================================
# RESEARCH PAPER ANALYSIS
# ==========================================

def analyze_papers(papers):

    github_stars = []


    papers_with_github = 0


    for paper in papers:

        stars = paper.get(
            "github_stars"
        )


        if stars is not None:

            github_stars.append(
                stars
            )


        if paper.get(
            "github_url"
        ):

            papers_with_github += 1


    top_papers = sorted(

        papers,

        key=lambda paper:

        paper.get(
            "github_stars"
        )

        or 0,

        reverse=True

    )[:10]


    top_paper_data = []


    for paper in top_papers:

        top_paper_data.append(

            {

                "title":

                    paper.get(
                        "title",
                        "Unknown"
                    ),

                "github_stars":

                    paper.get(
                        "github_stars",
                        0
                    ),

                "github_url":

                    paper.get(
                        "github_url"
                    )

            }

        )


    return {

        "total_papers":

            len(papers),


        "papers_with_github":

            papers_with_github,


        "papers_with_star_data":

            len(github_stars),


        "average_github_stars":

            round(

                sum(github_stars)

                /

                len(github_stars),

                2

            )

            if github_stars

            else 0,


        "top_papers":

            top_paper_data

    }


# ==========================================
# STARTUP ANALYSIS
# ==========================================

def analyze_startups(startups):

    startup_names = []


    for startup in startups:

        name = get_nested_value(

            startup,

            [

                "content",

                "name"

            ]

        )


        if not name:

            name = startup.get(
                "name"
            )


        if name:

            startup_names.append(
                name
            )


    return {

        "total_startups":

            len(startups),


        "sample_startups":

            startup_names[:20]

    }


# ==========================================
# PRODUCT ANALYSIS
# ==========================================

def analyze_products(products):

    brands = []


    product_names = []


    for product in products:

        brand = get_nested_value(

            product,

            [

                "content",

                "brand"

            ]

        )


        if not brand:

            brand = product.get(
                "brand"
            )


        if brand:

            brands.append(
                brand
            )


        name = get_nested_value(

            product,

            [

                "content",

                "name"

            ]

        )


        if not name:

            name = product.get(
                "name"
            )


        if name:

            product_names.append(
                name
            )


    brand_counts = Counter(
        brands
    )


    return {

        "total_products":

            len(products),


        "top_brands":

            brand_counts.most_common(
                10
            ),


        "sample_products":

            product_names[:20]

    }


# ==========================================
# NEWS ANALYSIS
# ==========================================

def analyze_news(news):

    sources = []


    headlines = []


    for article in news:

        source = get_nested_value(

            article,

            [

                "source",

                "name"

            ]

        )


        if source:

            sources.append(
                source
            )


        title = get_nested_value(

            article,

            [

                "content",

                "title"

            ]

        )


        if title:

            headlines.append(
                title
            )


    source_counts = Counter(
        sources
    )


    return {

        "total_news":

            len(news),


        "news_by_source":

            dict(
                source_counts
            ),


        "latest_headlines":

            headlines[:20]

    }


# ==========================================
# JOB ANALYSIS
# ==========================================

def analyze_jobs(jobs):

    companies = []


    roles = []


    remote_jobs = 0


    for job in jobs:

        company = get_nested_value(

            job,

            [

                "content",

                "company"

            ]

        )


        if company:

            companies.append(
                company
            )


        role = get_nested_value(

            job,

            [

                "content",

                "role_family"

            ]

        )


        if role:

            roles.append(
                role
            )


        is_remote = get_nested_value(

            job,

            [

                "content",

                "is_remote"

            ],

            False

        )


        if is_remote:

            remote_jobs += 1


    return {

        "total_jobs":

            len(jobs),


        "jobs_by_company":

            dict(

                Counter(
                    companies
                )

            ),


        "jobs_by_role":

            dict(

                Counter(
                    roles
                )

            ),


        "remote_jobs":

            remote_jobs

    }


# ==========================================
# BUILD COMPLETE DATA SUMMARY
# ==========================================

def build_data_summary():

    print(

        "\nLoading collected datasets..."

    )


    papers = load_json(

        DATA_FILES[
            "research_papers"
        ]

    )


    startups = load_json(

        DATA_FILES[
            "startups"
        ]

    )


    products = load_json(

        DATA_FILES[
            "products"
        ]

    )


    news = load_json(

        DATA_FILES[
            "news"
        ]

    )


    jobs = load_json(

        DATA_FILES[
            "jobs"
        ]

    )


    summary = {

        "generated_at":

            datetime.now(

                timezone.utc

            ).isoformat(),


        "research_papers":

            analyze_papers(
                papers
            ),


        "startups":

            analyze_startups(
                startups
            ),


        "products":

            analyze_products(
                products
            ),


        "news":

            analyze_news(
                news
            ),


        "jobs":

            analyze_jobs(
                jobs
            )

    }


    return summary


# ==========================================
# CREATE AI PROMPT
# ==========================================

def create_intelligence_prompt(
    summary
):

    summary_json = json.dumps(

        summary,

        indent=2,

        ensure_ascii=False

    )


    prompt = f"""

You are an AI Data Intelligence Agent.

Analyze the following collected intelligence
data and generate a concise but useful
business and technology intelligence report.

IMPORTANT RULES:

1. Use ONLY the supplied data.
2. Do not invent companies, statistics,
   trends, or events.
3. Clearly separate facts from inferences.
4. If the available data is insufficient,
   explicitly say so.
5. Focus on actionable insights.

DATA SUMMARY:

{summary_json}

Generate your report using exactly these
sections:

1. EXECUTIVE SUMMARY

2. RESEARCH TRENDS

3. GITHUB AND OPEN-SOURCE SIGNALS

4. STARTUP AND PRODUCT SIGNALS

5. AI NEWS TRENDS

6. AI JOB MARKET SIGNALS

7. CROSS-DOMAIN INSIGHTS

8. TOP OPPORTUNITIES

9. RISKS AND LIMITATIONS

Keep the report clear and concise.

"""


    return prompt


# ==========================================
# GENERATE INTELLIGENCE REPORT
# ==========================================

async def generate_intelligence_report():

    print(

        "\n" + "=" * 60

    )

    print(

        "AI INTELLIGENCE AGENT"

    )

    print(

        "=" * 60

    )


    # --------------------------------------
    # BUILD SUMMARY
    # --------------------------------------

    summary = build_data_summary()


    print(

        "\nDataset summary created."

    )


    print(

        f"Research papers: "
        f"{summary['research_papers']['total_papers']}"

    )


    print(

        f"Startups: "
        f"{summary['startups']['total_startups']}"

    )


    print(

        f"Products: "
        f"{summary['products']['total_products']}"

    )


    print(

        f"News articles: "
        f"{summary['news']['total_news']}"

    )


    print(

        f"Jobs: "
        f"{summary['jobs']['total_jobs']}"

    )


    # --------------------------------------
    # CREATE PROMPT
    # --------------------------------------

    prompt = create_intelligence_prompt(
        summary
    )


    print(

        "\nSending summary to "
        "LLM Intelligence Agent..."

    )


    # --------------------------------------
    # CALL LLM
    # --------------------------------------

    llm_result = (

        await generate_ai_response(
            prompt
        )

    )


    # --------------------------------------
    # CREATE FINAL REPORT
    # --------------------------------------

    report = {

        "generatedAt":

            datetime.now(

                timezone.utc

            ).isoformat(),


        "llmProvider":

            llm_result[
                "provider"
            ],


        "dataSummary":

            summary,


        "intelligenceReport":

            llm_result[
                "response"
            ]

    }


    # --------------------------------------
    # SAVE REPORT
    # --------------------------------------

    output_file = Path(

        "data/output/"
        "intelligence_report.json"

    )


    output_file.parent.mkdir(

        parents=True,

        exist_ok=True

    )


    with open(

        output_file,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            report,

            file,

            indent=4,

            ensure_ascii=False

        )


    print(

        "\n" + "=" * 60

    )

    print(

        "INTELLIGENCE REPORT GENERATED"

    )

    print(

        "=" * 60

    )


    print(

        f"\nProvider used: "
        f"{llm_result['provider']}"

    )


    print(

        f"\nSaved to: "
        f"{output_file}"

    )


    return report