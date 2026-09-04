import json
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Data Intelligence",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# DATA LOADING
# ============================================================

DATA_DIRECTORY = Path("data/output")

UNIFIED_FILE = (
    DATA_DIRECTORY /
    "unified_intelligence_data.json"
)


@st.cache_data
def load_data():

    if not UNIFIED_FILE.exists():
        return None

    with open(
        UNIFIED_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


data = load_data()


if data is None:

    st.error(
        "Data file not found. "
        "Please run run_export.py first."
    )

    st.stop()


datasets = data.get(
    "datasets",
    {}
)

statistics = data.get(
    "statistics",
    {}
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_record_count(name):

    return (
        statistics
        .get(name, {})
        .get("record_count", 0)
    )


def safe_dataframe(records):

    if not records:
        return pd.DataFrame()

    try:

        return pd.json_normalize(records)

    except Exception:

        return pd.DataFrame(records)


def find_column(df, possible_names):

    for name in possible_names:

        if name in df.columns:

            return name

    return None


# ============================================================
# HEADER
# ============================================================

st.title(
    "🤖 AI Data Intelligence Pipeline"
)

st.caption(
    "Multi-source AI intelligence system for "
    "research, startups, products, news and jobs"
)


# ============================================================
# OVERVIEW METRICS
# ============================================================

st.divider()

st.subheader(
    "📊 Intelligence Overview"
)


col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "Research Papers",
    get_record_count("research_papers")
)

col2.metric(
    "Startups",
    get_record_count("startups")
)

col3.metric(
    "Products",
    get_record_count("products")
)

col4.metric(
    "AI News",
    get_record_count("news")
)

col5.metric(
    "AI Jobs",
    get_record_count("jobs")
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🤖 Navigation"
)

page = st.sidebar.radio(

    "Choose a section",

    [
        "AI Intelligence Report",
        "Research Papers",
        "Startups",
        "Products",
        "AI News",
        "AI Jobs",
        "Data Summary"
    ]
)


# ============================================================
# AI INTELLIGENCE REPORT
# ============================================================

if page == "AI Intelligence Report":

    st.header(
        "🧠 AI Intelligence Report"
    )


    intelligence = datasets.get(
        "intelligence_report",
        {}
    )


    if intelligence:

        provider = intelligence.get(
            "llmProvider",
            "Unknown"
        )


        report = intelligence.get(
            "intelligenceReport",
            "No report available."
        )


        st.success(
            f"Generated using: {provider}"
        )


        st.markdown(
            report
        )


        summary = intelligence.get(
            "dataSummary",
            {}
        )


        if summary:

            with st.expander(
                "View Data Summary Used for Analysis"
            ):

                st.json(summary)


    else:

        st.warning(
            "No intelligence report found."
        )


# ============================================================
# RESEARCH PAPERS
# ============================================================

elif page == "Research Papers":

    st.header(
        "📄 Research Intelligence"
    )


    papers = datasets.get(
        "research_papers",
        []
    )


    df = safe_dataframe(
        papers
    )


    st.metric(
        "Total Papers",
        len(df)
    )


    if not df.empty:

        search = st.text_input(
            "🔍 Search research papers"
        )


        title_column = find_column(

            df,

            [
                "title",
                "content.title"
            ]
        )


        if search and title_column:

            df = df[

                df[title_column]

                .astype(str)

                .str.contains(

                    search,

                    case=False,

                    na=False
                )

            ]


        stars_column = find_column(

            df,

            [
                "github_stars",
                "content.github_stars"
            ]
        )


        if stars_column:

            st.subheader(
                "⭐ Top Open-Source Research"
            )


            top_papers = (

                df.sort_values(

                    by=stars_column,

                    ascending=False

                )

                .head(10)

            )


            display_columns = [

                column

                for column in [

                    title_column,
                    stars_column

                ]

                if column
            ]


            st.dataframe(

                top_papers[
                    display_columns
                ],

                use_container_width=True

            )


        st.subheader(
            "All Research Papers"
        )


        st.dataframe(

            df,

            use_container_width=True,

            height=500

        )


# ============================================================
# STARTUPS
# ============================================================

elif page == "Startups":

    st.header(
        "🚀 Startup Intelligence"
    )


    startups = datasets.get(
        "startups",
        []
    )


    df = safe_dataframe(
        startups
    )


    st.metric(
        "Total Startups",
        len(df)
    )


    if not df.empty:

        search = st.text_input(
            "🔍 Search startups"
        )


        name_column = find_column(

            df,

            [
                "name",
                "content.name",
                "company",
                "content.company"
            ]
        )


        if search and name_column:

            df = df[

                df[name_column]

                .astype(str)

                .str.contains(

                    search,

                    case=False,

                    na=False
                )

            ]


        st.dataframe(

            df,

            use_container_width=True,

            height=600

        )


# ============================================================
# PRODUCTS
# ============================================================

elif page == "Products":

    st.header(
        "🛍️ Product Intelligence"
    )


    products = datasets.get(
        "products",
        []
    )


    df = safe_dataframe(
        products
    )


    st.metric(
        "Total Products",
        len(df)
    )


    if not df.empty:

        search = st.text_input(
            "🔍 Search products"
        )


        name_column = find_column(

            df,

            [
                "name",
                "title",
                "content.name",
                "content.title"
            ]
        )


        if search and name_column:

            df = df[

                df[name_column]

                .astype(str)

                .str.contains(

                    search,

                    case=False,

                    na=False
                )

            ]


        st.dataframe(

            df,

            use_container_width=True,

            height=600

        )


# ============================================================
# AI NEWS
# ============================================================

elif page == "AI News":

    st.header(
        "📰 AI News Intelligence"
    )


    news = datasets.get(
        "news",
        []
    )


    df = safe_dataframe(
        news
    )


    st.metric(
        "Total News Articles",
        len(df)
    )


    if not df.empty:

        title_column = find_column(

            df,

            [
                "title",
                "content.title"
            ]
        )


        link_column = find_column(

            df,

            [
                "url",
                "link",
                "content.url"
            ]
        )


        source_column = find_column(

            df,

            [
                "source.name",
                "source",
                "content.source"
            ]
        )


        for _, article in df.iterrows():

            title = (

                article.get(
                    title_column,
                    "Untitled"
                )

                if title_column

                else "Untitled"

            )


            with st.container():

                st.subheader(
                    str(title)
                )


                if source_column:

                    st.caption(

                        f"Source: "
                        f"{article.get(source_column)}"

                    )


                if link_column:

                    link = article.get(
                        link_column
                    )

                    if pd.notna(link):

                        st.link_button(
                            "Read Article",
                            str(link)
                        )


                st.divider()


# ============================================================
# AI JOBS
# ============================================================

elif page == "AI Jobs":

    st.header(
        "💼 AI Job Intelligence"
    )


    jobs = datasets.get(
        "jobs",
        []
    )


    df = safe_dataframe(
        jobs
    )


    st.metric(
        "Total AI Jobs",
        len(df)
    )


    if not df.empty:

        company_column = find_column(

            df,

            [
                "company",
                "content.company"
            ]
        )


        role_column = find_column(

            df,

            [
                "role_family",
                "title",
                "content.role_family",
                "content.title"
            ]
        )


        if company_column:

            st.subheader(
                "Jobs by Company"
            )


            company_counts = (

                df[company_column]

                .value_counts()

                .head(10)

            )


            st.bar_chart(
                company_counts
            )


        st.subheader(
            "Available AI Jobs"
        )


        display_columns = [

            column

            for column in [

                company_column,
                role_column

            ]

            if column
        ]


        if display_columns:

            st.dataframe(

                df[
                    display_columns
                ],

                use_container_width=True,

                height=500

            )

        else:

            st.dataframe(

                df,

                use_container_width=True

            )


# ============================================================
# DATA SUMMARY
# ============================================================

elif page == "Data Summary":

    st.header(
        "📊 Dataset Summary"
    )


    summary_rows = []


    for name, stats in statistics.items():

        summary_rows.append(

            {

                "Dataset":

                    name.replace(

                        "_",

                        " "

                    ).title(),


                "Records":

                    stats.get(

                        "record_count",

                        0

                    )

            }

        )


    summary_df = pd.DataFrame(
        summary_rows
    )


    st.dataframe(

        summary_df,

        use_container_width=True

    )


    st.subheader(
        "Dataset Distribution"
    )


    if not summary_df.empty:

        chart_data = (

            summary_df

            .set_index(

                "Dataset"

            )

        )


        st.bar_chart(
            chart_data
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(

    "AI Data Intelligence Pipeline • "
    "Automated Multi-Agent Intelligence System"

)