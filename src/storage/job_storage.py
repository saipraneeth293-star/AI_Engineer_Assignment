import json

from pathlib import Path


OUTPUT_FILE = Path(
    "data/output/jobs.json"
)


def save_jobs(jobs):

    OUTPUT_FILE.parent.mkdir(

        parents=True,

        exist_ok=True
    )


    data = [

        job.model_dump()

        for job in jobs
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

        f"Saved {len(jobs)} "
        f"job records"

    )