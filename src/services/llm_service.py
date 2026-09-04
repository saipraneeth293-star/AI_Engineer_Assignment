import os
import asyncio
import random

from dotenv import load_dotenv

from google import genai
from groq import Groq
from openai import AsyncOpenAI


load_dotenv()


# ==========================================
# API KEYS
# ==========================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


# ==========================================
# SETTINGS
# ==========================================

MAX_RETRIES = 3

BASE_DELAY = 2


# ==========================================
# RETRY WITH EXPONENTIAL BACKOFF
# Only retry temporary errors
# ==========================================

async def retry_with_backoff(function, *args, **kwargs):

    last_error = None

    for attempt in range(MAX_RETRIES):

        try:

            return await function(
                *args,
                **kwargs
            )

        except Exception as error:

            last_error = error

            error_text = str(error)

            # Do not retry permanent errors
            permanent_errors = [

                "404",

                "401",

                "402",

                "Insufficient Balance",

                "model_not_found",

                "NOT_FOUND"

            ]

            if any(

                item.lower()
                in error_text.lower()

                for item in permanent_errors

            ):

                raise error


            if attempt == MAX_RETRIES - 1:

                raise error


            delay = (

                BASE_DELAY
                * (2 ** attempt)
                + random.uniform(0, 1)

            )

            print(
                f"Temporary error. "
                f"Retrying in {delay:.2f} seconds..."
            )

            await asyncio.sleep(delay)


    raise last_error


# ==========================================
# GEMINI
# ==========================================

async def call_gemini(prompt):

    if not GEMINI_API_KEY:

        raise ValueError(
            "Gemini API key is missing"
        )


    client = genai.Client(

        api_key=GEMINI_API_KEY

    )


    def generate():

        response = (

            client.models.generate_content(

                model="gemini-3.6-flash",

                contents=prompt

            )

        )


        return response.text


    return await asyncio.to_thread(
        generate
    )


# ==========================================
# GROQ
# ==========================================

async def call_groq(prompt):

    if not GROQ_API_KEY:

        raise ValueError(
            "Groq API key is missing"
        )


    client = Groq(

        api_key=GROQ_API_KEY

    )


    def generate():

        completion = (

            client.chat.completions.create(

                # Current alternative model
                model="openai/gpt-oss-20b",

                messages=[

                    {

                        "role": "user",

                        "content": prompt

                    }

                ],

                temperature=0.3,

                max_completion_tokens=1000

            )

        )


        return (

            completion
            .choices[0]
            .message
            .content

        )


    return await asyncio.to_thread(
        generate
    )


# ==========================================
# DEEPSEEK
# ==========================================

async def call_deepseek(prompt):

    if not DEEPSEEK_API_KEY:

        raise ValueError(
            "DeepSeek API key is missing"
        )


    client = AsyncOpenAI(

        api_key=DEEPSEEK_API_KEY,

        base_url=(
            "https://api.deepseek.com"
        )

    )


    response = (

        await client
        .chat
        .completions
        .create(

            model="deepseek-chat",

            messages=[

                {

                    "role": "user",

                    "content": prompt

                }

            ],

            temperature=0.3,

            max_tokens=1000

        )

    )


    return (

        response
        .choices[0]
        .message
        .content

    )


# ==========================================
# MAIN FALLBACK SYSTEM
# ==========================================

async def generate_ai_response(prompt):

    providers = [

        (
            "Gemini Flash",
            call_gemini,
            GEMINI_API_KEY
        ),

        (
            "Groq GPT-OSS",
            call_groq,
            GROQ_API_KEY
        ),

        (
            "DeepSeek",
            call_deepseek,
            DEEPSEEK_API_KEY
        )

    ]


    errors = []


    for (

        provider_name,
        provider_function,
        api_key

    ) in providers:


        # Skip missing keys

        if not api_key:

            print(

                f"\nSkipping "
                f"{provider_name}: "
                f"No API key"

            )

            continue


        print(

            f"\nTrying "
            f"{provider_name}..."

        )


        try:

            response = (

                await retry_with_backoff(

                    provider_function,

                    prompt

                )

            )


            print(

                f"{provider_name} "
                f"successful!"

            )


            return {

                "provider": provider_name,

                "response": response

            }


        except Exception as error:

            error_message = (

                f"{provider_name}: "
                f"{str(error)}"

            )

            errors.append(
                error_message
            )


            print(

                f"{provider_name} "
                f"failed: {error}"

            )


    raise RuntimeError(

        "\nAll LLM providers failed.\n\n"

        + "\n".join(errors)

    )