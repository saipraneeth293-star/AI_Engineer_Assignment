import json

from pathlib import Path


OUTPUT_FILE = Path(
    "data/output/products.json"
)


def save_products(products):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = [

        product.model_dump()

        for product in products

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
        f"Saved {len(products)} "
        f"product records"
    )