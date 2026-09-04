import asyncio

from src.services.llm_service import (
    generate_ai_response
)


async def main():

    prompt = """

You are an AI data intelligence assistant.

Explain in three short points what an AI data
intelligence pipeline does.

"""


    result = await generate_ai_response(

        prompt
    )


    print("\n" + "=" * 60)

    print(
        "LLM RESPONSE"
    )

    print("=" * 60)


    print(

        f"\nProvider: "
        f"{result['provider']}"

    )


    print(

        f"\nResponse:\n"
        f"{result['response']}"

    )


if __name__ == "__main__":

    asyncio.run(main())