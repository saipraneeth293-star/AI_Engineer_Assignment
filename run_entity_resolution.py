import json
from pathlib import Path

from src.services.entity_resolution import (
    resolve_entities
)


STARTUP_FILE = Path(
    "data/output/startups.json"
)

PRODUCT_FILE = Path(
    "data/output/products.json"
)

JOB_FILE = Path(
    "data/output/jobs.json"
)


OUTPUT_FILE = Path(
    "data/output/entity_mapping_log.json"
)


def load_json(path):

    if not path.exists():

        print(
            f"File not found: {path}"
        )

        return []

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    print("=" * 60)

    print(
        "ENTITY RESOLUTION"
    )

    print("=" * 60)


    names = []


    # ======================================
    # EXTRACT STARTUP NAMES
    # ======================================

    startups = load_json(
        STARTUP_FILE
    )


    for startup in startups:

        try:

            name = (

                startup
                .get("content", {})
                .get("name")
            )

            if name:

                names.append(
                    name
                )

        except Exception:

            pass


    # ======================================
    # EXTRACT PRODUCT BRANDS
    # ======================================

    products = load_json(
        PRODUCT_FILE
    )


    for product in products:

        try:

            name = (

                product
                .get("content", {})
                .get("brand")
            )

            if name:

                names.append(
                    name
                )

        except Exception:

            pass


    # ======================================
    # EXTRACT JOB COMPANIES
    # ======================================

    jobs = load_json(
        JOB_FILE
    )


    for job in jobs:

        try:

            name = (

                job
                .get("content", {})
                .get("company")
            )

            if name:

                names.append(
                    name
                )

        except Exception:

            pass


    print(
        f"\nRaw entities found: "
        f"{len(names)}"
    )


    # ======================================
    # RESOLVE ENTITIES
    # ======================================

    _, mapping_log = resolve_entities(
        names
    )


    print(
        f"Unique entities resolved: "
        f"{len(mapping_log)}"
    )


    # ======================================
    # SAVE LOG
    # ======================================

    OUTPUT_FILE.parent.mkdir(

        parents=True,

        exist_ok=True
    )


    with open(

        OUTPUT_FILE,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            mapping_log,

            file,

            indent=4,

            ensure_ascii=False
        )


    print(

        f"\nSaved entity mapping log to: "
        f"{OUTPUT_FILE}"

    )


if __name__ == "__main__":

    main()