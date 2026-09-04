import re
from datetime import datetime, timezone


# ==========================================
# KNOWN ENTITY ALIASES
# ==========================================

ENTITY_ALIASES = {

    "open ai": "OpenAI",
    "openai inc": "OpenAI",
    "openai, inc": "OpenAI",

    "huggingface": "Hugging Face",
    "hugging face inc": "Hugging Face",

    "anthropic ai": "Anthropic",
    "anthropic pbc": "Anthropic",

    "google inc": "Google",
    "google llc": "Google",

    "microsoft corporation": "Microsoft",
    "microsoft corp": "Microsoft",

    "meta platforms": "Meta",
    "meta platforms inc": "Meta",

    "amazon.com": "Amazon",
    "amazon inc": "Amazon",

    "scale ai inc": "Scale AI",
}


# ==========================================
# NORMALIZE RAW TEXT
# ==========================================

def normalize_name(name):

    if not name:

        return ""

    name = name.lower()

    name = re.sub(
        r"[^a-z0-9\s]",
        " ",
        name
    )

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name.strip()


# ==========================================
# REMOVE COMMON COMPANY SUFFIXES
# ==========================================

def remove_company_suffixes(name):

    suffixes = [

        "inc",

        "incorporated",

        "llc",

        "ltd",

        "limited",

        "corp",

        "corporation",

        "company",

        "co",

        "pbc",
    ]

    words = name.split()

    while words and words[-1] in suffixes:

        words.pop()

    return " ".join(words)


# ==========================================
# RESOLVE SINGLE ENTITY
# ==========================================

def resolve_entity(raw_name):

    if not raw_name:

        return None, None


    normalized = normalize_name(
        raw_name
    )


    normalized = remove_company_suffixes(
        normalized
    )


    # Check known aliases

    if normalized in ENTITY_ALIASES:

        canonical_name = ENTITY_ALIASES[
            normalized
        ]

        confidence = 1.0

    else:

        # Default canonical form

        canonical_name = " ".join(

            word.capitalize()

            for word in normalized.split()

        )

        confidence = 0.80


    return canonical_name, confidence


# ==========================================
# CREATE MAPPING LOG ENTRY
# ==========================================

def create_mapping_log(

    raw_name,

    canonical_name,

    confidence

):

    return {

        "rawName": raw_name,

        "canonicalName": canonical_name,

        "confidence": confidence,

        "resolvedAt": (

            datetime.now(
                timezone.utc
            ).isoformat()

        )
    }


# ==========================================
# RESOLVE MULTIPLE NAMES
# ==========================================

def resolve_entities(names):

    resolved_entities = {}

    mapping_log = []


    for raw_name in names:

        if not raw_name:

            continue


        if raw_name in resolved_entities:

            continue


        canonical_name, confidence = (

            resolve_entity(
                raw_name
            )

        )


        resolved_entities[
            raw_name
        ] = canonical_name


        mapping_log.append(

            create_mapping_log(

                raw_name,

                canonical_name,

                confidence

            )

        )


    return (

        resolved_entities,

        mapping_log

    )