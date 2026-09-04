import os
import re
import ssl

import aiohttp
import certifi


GITHUB_PATTERN = (
    r"https?://github\.com/"
    r"[\w.-]+/[\w.-]+"
)


def extract_github_urls(text: str) -> list[str]:

    if not text:
        return []

    urls = re.findall(
        GITHUB_PATTERN,
        text
    )

    clean_urls = []

    for url in urls:

        url = url.rstrip(
            ".,);]}>"
        )

        if url not in clean_urls:

            clean_urls.append(url)

    return clean_urls


async def get_github_stars(
    session,
    github_url: str
):

    match = re.search(
        r"github\.com/([^/]+)/([^/#?]+)",
        github_url
    )

    if not match:
        return None

    owner = match.group(1)

    repository = match.group(2)

    repository = repository.replace(
        ".git",
        ""
    )

    api_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository}"
    )

    try:

        async with session.get(
            api_url
        ) as response:

            # Successful request
            if response.status == 200:

                data = await response.json()

                return data.get(
                    "stargazers_count"
                )

            # Invalid authentication
            if response.status == 401:

                print(
                    "\nERROR: GitHub token is invalid "
                    "or expired."
                )

                return None

            # Rate limit
            if response.status == 403:

                remaining = response.headers.get(
                    "X-RateLimit-Remaining"
                )

                if remaining == "0":

                    print(
                        "\nGitHub API rate limit reached."
                    )

                return None

            # Too many requests
            if response.status == 429:

                print(
                    "\nGitHub returned 429: "
                    "Too many requests."
                )

                return None

            print(
                f"GitHub API error: "
                f"{response.status}"
            )

            return None

    except Exception as error:

        print(
            f"GitHub request failed: "
            f"{error}"
        )

        return None


async def create_github_session():

    ssl_context = ssl.create_default_context(
        cafile=certifi.where()
    )

    connector = aiohttp.TCPConnector(
        ssl=ssl_context
    )

    timeout = aiohttp.ClientTimeout(
        total=30
    )

    headers = {

        "Accept":
        "application/vnd.github+json",

        "User-Agent":
        "AI-Data-Intelligence-Pipeline"
    }

    github_token = os.getenv(
        "GITHUB_TOKEN"
    )

    # Only use the token if it exists
    # and isn't a placeholder.
    if (
        github_token
        and "your_" not in github_token.lower()
    ):

        headers["Authorization"] = (
            f"Bearer {github_token.strip()}"
        )

        print(
            "GitHub authentication enabled."
        )

    else:

        print(
            "WARNING: No valid GitHub token found. "
            "Using unauthenticated API access."
        )

    return aiohttp.ClientSession(

        connector=connector,

        timeout=timeout,

        headers=headers
    )