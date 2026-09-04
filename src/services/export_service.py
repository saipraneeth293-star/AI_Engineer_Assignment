import json

from pathlib import Path
from datetime import datetime, timezone


# ==========================================
# FILE LOCATIONS
# ==========================================

DATA_DIRECTORY = Path(
    "data/output"
)


FILES = {

    "research_papers":
        "research_papers.json",

    "startups":
        "startups.json",

    "products":
        "products.json",

    "news":
        "news.json",

    "jobs":
        "jobs.json",

    "intelligence_report":
        "intelligence_report.json"

}


# ==========================================
# LOAD JSON SAFELY
# ==========================================

def load_json(filename):

    file_path = (
        DATA_DIRECTORY / filename
    )


    if not file_path.exists():

        print(
            f"Warning: Missing file: "
            f"{file_path}"
        )

        return None


    try:

        with open(

            file_path,

            "r",

            encoding="utf-8"

        ) as file:

            return json.load(file)


    except Exception as error:

        print(

            f"Error loading "
            f"{filename}: {error}"

        )

        return None


# ==========================================
# CREATE DATA STATISTICS
# ==========================================

def create_statistics(datasets):

    statistics = {}


    for name, data in datasets.items():

        if isinstance(data, list):

            statistics[name] = {

                "record_count":

                    len(data)

            }


        elif isinstance(data, dict):

            statistics[name] = {

                "record_count":

                    1

            }


        else:

            statistics[name] = {

                "record_count":

                    0

            }


    return statistics


# ==========================================
# CREATE UNIFIED EXPORT
# ==========================================

def create_unified_export():

    print("\n" + "=" * 60)

    print(
        "CREATING UNIFIED DATA EXPORT"
    )

    print("=" * 60)


    datasets = {}


    # --------------------------------------
    # LOAD ALL DATASETS
    # --------------------------------------

    for dataset_name, filename in FILES.items():

        print(

            f"\nLoading "
            f"{dataset_name}..."

        )


        data = load_json(
            filename
        )


        if data is not None:

            datasets[
                dataset_name
            ] = data

        else:

            datasets[
                dataset_name
            ] = []


    # --------------------------------------
    # CREATE STATISTICS
    # --------------------------------------

    statistics = create_statistics(
        datasets
    )


    # --------------------------------------
    # CREATE FINAL STRUCTURE
    # --------------------------------------

    unified_data = {

        "generated_at":

            datetime.now(

                timezone.utc

            ).isoformat(),


        "project":

            "AI Data Intelligence Pipeline",


        "statistics":

            statistics,


        "datasets":

            datasets

    }


    # --------------------------------------
    # SAVE
    # --------------------------------------

    output_file = (

        DATA_DIRECTORY

        /

        "unified_intelligence_data.json"

    )


    with open(

        output_file,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            unified_data,

            file,

            indent=2,

            ensure_ascii=False

        )


    print("\n" + "=" * 60)

    print(
        "UNIFIED EXPORT COMPLETED"
    )

    print("=" * 60)


    print(

        f"\nSaved to:\n"
        f"{output_file}"

    )


    print(
        "\nDataset statistics:"
    )


    for name, stats in statistics.items():

        print(

            f"- {name}: "
            f"{stats['record_count']} records"

        )


    return unified_data