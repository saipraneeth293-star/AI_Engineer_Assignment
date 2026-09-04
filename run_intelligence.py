import asyncio

from src.services.intelligence_agent import (
    generate_intelligence_report
)


async def main():

    report = (

        await generate_intelligence_report()

    )


    print("\n")

    print("=" * 60)

    print(
        "AI INTELLIGENCE REPORT"
    )

    print("=" * 60)


    print(

        report[
            "intelligenceReport"
        ]

    )


if __name__ == "__main__":

    asyncio.run(main())