import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "csv_data" / "ScreenAnalysis.csv"
APP_NAME = os.getenv("APP_NAME", "MyVibeProject")
AGE_GROUPS = ("16-24", "25-34", "35-44", "45+")


@st.cache_data(show_spinner=False)
def load_survey() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH).dropna(axis=1, how="all")
    required_columns = {
        "user_id",
        "age",
        "gender",
        "occupation",
        "screen_time_hours",
        "sleep_quality_1_5",
        "stress_level_0_10",
    }
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(f"Survey CSV is missing columns: {', '.join(sorted(missing_columns))}")

    data["age_group"] = pd.cut(
        data["age"],
        bins=[15, 24, 34, 44, float("inf")],
        labels=AGE_GROUPS,
    )
    return data


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
        .stApp {
            background-color: #0E1525;
            color: #F1F5F9;
        }
        html, body, [class*="st-"] { font-family: 'Manrope', sans-serif; }
        h1, h2, h3 { color: #F8FAFC; letter-spacing: 0; }
        h1 { font-weight: 800; }
        div[data-testid="stSidebar"] { background-color: #111C2E !important; }
        [data-testid="stMetric"] {
            background: #192438;
            padding: 18px;
            border: 1px solid #29374D;
            border-radius: 12px;
        }
        [data-testid="stMetricLabel"] { color: #A7B5C7; }
        [data-testid="stMetricValue"] { color: #F1F5F9; }
        code, [data-testid="stMetricDelta"] { font-family: 'DM Mono', monospace; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def add_sidebar_filters(page_key: str) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]:
    data = load_survey()
    with st.sidebar:
        st.markdown(f"## {APP_NAME}")
        st.caption("SCREEN USE / WELLNESS")
        st.divider()
        st.subheader("Participant criteria")
        age_options = ["All ages", *AGE_GROUPS]
        age_group = st.selectbox("Age group", age_options, key=f"{page_key}_age")

        gender_options = ["All genders", *sorted(data["gender"].dropna().unique())]
        gender = st.selectbox("Gender", gender_options, key=f"{page_key}_gender")

        occupation_options = ["All occupations", *sorted(data["occupation"].dropna().unique())]
        occupation = st.selectbox(
            "Occupation", occupation_options, key=f"{page_key}_occupation"
        )

    matches = pd.Series(True, index=data.index)
    if age_group != "All ages":
        matches &= data["age_group"].eq(age_group).fillna(False)
    if gender != "All genders":
        matches &= data["gender"].eq(gender)
    if occupation != "All occupations":
        matches &= data["occupation"].eq(occupation)

    selected = {"age_group": age_group, "gender": gender, "occupation": occupation}
    return data, data.loc[matches].copy(), selected