import json
from pathlib import Path


OUTPUT_FILE = Path(
    "data/output/research_papers.json"
)


def save_papers(papers):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = [
        paper.model_dump()
        for paper in papers
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
        f"Saved {len(papers)} papers"
    )