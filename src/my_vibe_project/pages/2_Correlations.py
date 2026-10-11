import altair as alt
import pandas as pd
import streamlit as st

from my_vibe_project.survey_data import APP_NAME, add_sidebar_filters, apply_styles


st.set_page_config(page_title=f"{APP_NAME} | Correlations", layout="wide")
apply_styles()
_, filtered, selected = add_sidebar_filters("correlations")

st.caption("SURVEY ANALYSIS  /  CORRELATIONS")
st.title("Screen time correlations")
st.write(
    "Compare daily screen time with sleep quality and stress for participants matching "
    "the selected criteria."
)
st.caption(
    "Pearson correlation describes a linear association, not causation. Sleep quality "
    "is self-reported on a 1–5 scale; survey results are not clinical assessments."
)

if filtered.empty:
    st.warning("No participants match these criteria. Change one or more sidebar selections.")
    st.stop()

criteria = [
    selected["age_group"],
    selected["gender"],
    selected["occupation"],
]
criteria_summary = " / ".join(value for value in criteria if not value.startswith("All "))
st.markdown(
    f"**{len(filtered):,} participants**"
    + (f" · {criteria_summary}" if criteria_summary else " · all participants")
)


def show_correlation(
    *,
    title="Screen time & sleep quality",
    outcome_column="sleep_quality_1_5",
    outcome_label="Sleep quality",
    scale="1–5",
) -> None:
    numeric_data = filtered[["screen_time_hours", outcome_column]].dropna().copy()
    correlation = numeric_data["screen_time_hours"].corr(numeric_data[outcome_column])

    st.subheader(title)
    metric_columns = st.columns(2)
    metric_columns[0].metric(
        "Pearson correlation",
        "—" if pd.isna(correlation) else f"{correlation:+.2f}",
    )
    metric_columns[1].metric("Participants", f"{len(numeric_data):,}")
    if pd.isna(correlation):
        st.caption("Correlation is unavailable for this selection because a measure has no variation.")
    elif correlation > 0:
        st.caption("Higher screen time is associated with higher values on this measure in this selection.")
    elif correlation < 0:
        st.caption("Higher screen time is associated with lower values on this measure in this selection.")
    else:
        st.caption("No linear association appears in this selection.")

    distinct_screen_times = numeric_data["screen_time_hours"].nunique()
    if len(numeric_data) < 2 or distinct_screen_times < 2:
        st.info("Not enough variation in this selection to chart a screen-time relationship.")
        return

    points = alt.Chart(numeric_data).mark_circle(size=38, opacity=0.35).encode(
        x=alt.X("screen_time_hours:Q", title="Daily screen time (hours)"),
        y=alt.Y(f"{outcome_column}:Q", title=f"{outcome_label} ({scale})"),
        tooltip=[
            alt.Tooltip("screen_time_hours:Q", title="Screen time (hours)", format=".1f"),
            alt.Tooltip(f"{outcome_column}:Q", title=f"{outcome_label} ({scale})"),
        ],
    )
    trend = (
        alt.Chart(numeric_data)
        .transform_regression("screen_time_hours", outcome_column)
        .mark_line(color="#187c70", strokeWidth=3)
        .encode(
            x=alt.X("screen_time_hours:Q"),
            y=alt.Y(f"{outcome_column}:Q"),
        )
    )
    st.altair_chart(
        (points + trend).properties(height=360),
        use_container_width=True,
    )
    st.caption(
        "Each point represents one participant. The line is a linear trend fitted "
        "to the individual records; it summarizes association and does not establish causation."
    )


show_correlation()
st.divider()
show_correlation(
    title="Screen time & stress",
    outcome_column="stress_level_0_10",
    outcome_label="Stress level",
    scale="0–10",
)
