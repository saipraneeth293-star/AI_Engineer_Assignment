import asyncio

from src.crawler.job_crawler import (
    get_jobs
)

from src.storage.job_storage import (
    save_jobs
)


async def main():

    jobs = await get_jobs()

    save_jobs(
        jobs
    )


    print(

        f"\nFINAL JOB COUNT: "
        f"{len(jobs)}"

    )


if __name__ == "__main__":

    asyncio.run(main())