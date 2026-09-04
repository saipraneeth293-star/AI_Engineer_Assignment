import json
from pathlib import Path


OUTPUT_FILE = Path(
    "data/output/startups.json"
)


def save_startups(startups):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = [

        startup.model_dump()

        for startup in startups

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
        f"Saved {len(startups)} "
        f"startup records"
    )