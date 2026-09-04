import asyncio

from src.crawler.product_crawler import get_products


from src.storage.product_storage import save_products


async def main():

    products = await get_products(
        total_products=1000
    )

    save_products(products)

    print(
        f"\nFINAL PRODUCT COUNT: "
        f"{len(products)}"
    )


if __name__ == "__main__":

    asyncio.run(main())