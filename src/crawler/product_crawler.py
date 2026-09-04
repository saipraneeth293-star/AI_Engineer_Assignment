import csv
import io
import ssl
from datetime import datetime, timezone

import aiohttp
import certifi

from src.models.product import (
    Product,
    ProductSource,
    ProductContent
)


PRODUCT_SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    "luminati-io/"
    "Google-Shopping-dataset-sample/"
    "main/"
    "Google-Shopping-dataset-sample.csv"
)


async def fetch_products():

    ssl_context = ssl.create_default_context(
        cafile=certifi.where()
    )

    connector = aiohttp.TCPConnector(
        ssl=ssl_context
    )

    timeout = aiohttp.ClientTimeout(
        total=120
    )

    headers = {
        "User-Agent":
        "AI-Data-Intelligence-Pipeline/1.0"
    }

    try:

        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        ) as session:

            print(
                "Downloading product dataset..."
            )

            async with session.get(
                PRODUCT_SOURCE_URL
            ) as response:

                print(
                    f"Product source status: "
                    f"{response.status}"
                )

                response.raise_for_status()

                csv_text = await response.text()

                reader = csv.DictReader(
                    io.StringIO(csv_text)
                )

                data = list(reader)

                print(
                    f"Downloaded "
                    f"{len(data)} raw products"
                )

                return data

    except Exception as error:

        print(
            f"Product download failed: {error}"
        )

        return []


def get_value(item, fields):

    for field in fields:

        value = item.get(field)

        if (
            value is not None
            and str(value).strip()
        ):

            return value

    return None


def convert_price(value):

    if value is None:
        return None

    try:

        cleaned_value = str(value)

        # Remove common currency symbols
        for character in [
            "$",
            "₹",
            "€",
            "£",
            ","
        ]:

            cleaned_value = (
                cleaned_value.replace(
                    character,
                    ""
                )
            )

        return float(
            cleaned_value.strip()
        )

    except (
        ValueError,
        TypeError
    ):

        return None


def parse_products(
    raw_data,
    total_products=1000
):

    products = []

    seen_products = set()

    collected_at = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    for item in raw_data:

        if len(products) >= total_products:
            break

        try:

            # -------------------------
            # PRODUCT NAME
            # -------------------------

            product_name = get_value(
                item,
                [
                    "title",
                    "name",
                    "product_name"
                ]
            )

            if not product_name:
                continue

            # -------------------------
            # SELLER / BRAND
            # -------------------------

            seller = get_value(
                item,
                [
                    "seller_name",
                    "brand",
                    "manufacturer"
                ]
            )

            # -------------------------
            # DUPLICATE CHECK
            # -------------------------

            duplicate_key = (
                f"{product_name}|"
                f"{seller or ''}"
            ).strip().lower()

            if duplicate_key in seen_products:
                continue

            seen_products.add(
                duplicate_key
            )

            # -------------------------
            # PRODUCT URL
            # -------------------------

            product_url = get_value(
                item,
                [
                    "url",
                    "product_url"
                ]
            )

            # -------------------------
            # DESCRIPTION
            # -------------------------

            description = get_value(
                item,
                [
                    "product_description",
                    "description"
                ]
            )

            # -------------------------
            # CATEGORY
            # -------------------------

            category = get_value(
                item,
                [
                    "tags",
                    "category",
                    "breadcrumbs"
                ]
            )

            # -------------------------
            # PRICE
            # -------------------------

            raw_price = get_value(
                item,
                [
                    "item_price",
                    "total_price",
                    "final_price",
                    "price"
                ]
            )

            price = convert_price(
                raw_price
            )

            # -------------------------
            # CURRENCY
            # -------------------------

            currency = get_value(
                item,
                [
                    "currency"
                ]
            )

            # -------------------------
            # CREATE PRODUCT
            # -------------------------

            product = Product(

                source=ProductSource(

                    name=(
                        "Google Shopping "
                        "Dataset Sample"
                    ),

                    url=(
                        product_url
                        if product_url
                        else PRODUCT_SOURCE_URL
                    )
                ),

                content=ProductContent(

                    productName=str(
                        product_name
                    ),

                    productUrl=product_url,

                    description=(
                        str(description)
                        if description
                        else None
                    ),

                    category=(
                        str(category)
                        if category
                        else None
                    ),

                    price=price,

                    currency=(
                        str(currency)
                        if currency
                        else None
                    )
                ),

                collectedAt=collected_at
            )

            products.append(
                product
            )

        except Exception as error:

            print(
                f"Skipping product: "
                f"{error}"
            )

    return products


async def get_products(
    total_products=1000
):

    print("\n" + "=" * 60)

    print(
        "PRODUCT DATA COLLECTION"
    )

    print("=" * 60)

    raw_data = await fetch_products()

    if not raw_data:

        print(
            "No product data collected."
        )

        return []

    products = parse_products(

        raw_data,

        total_products
    )

    print(
        f"\nUnique products collected: "
        f"{len(products)}"
    )

    return products