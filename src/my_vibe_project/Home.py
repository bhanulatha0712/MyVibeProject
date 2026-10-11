import streamlit as st

from my_vibe_project.survey_data import APP_NAME, add_sidebar_filters, apply_styles


st.set_page_config(page_title=f"{APP_NAME} | Participant Data", layout="wide")
apply_styles()
data, filtered, _ = add_sidebar_filters("data")

st.caption("SURVEY DATA  /  FILTERED PARTICIPANTS")
st.title("Participant data")
st.write("This dataset captures insights from 400 survey participants on how their daily screen usage relates to mental wellness.")

if filtered.empty:
    st.warning("No participants match these criteria. Change one or more sidebar selections.")
    st.stop()

metric_columns = st.columns(3)
metric_columns[0].metric("Matching participants", f"{len(filtered):,}")
metric_columns[1].metric("Missing data cells", f"{int(filtered.isna().sum().sum()):,}")
metric_columns[2].metric("Duplicate participant IDs", f"{int(filtered['user_id'].duplicated().sum()):,}")

st.download_button(
    "Download filtered CSV",
    data=filtered.drop(columns="age_group").to_csv(index=False).encode("utf-8"),
    file_name="screen-analysis-filtered.csv",
    mime="text/csv",
)
st.dataframe(filtered, hide_index=True, use_container_width=True, height=600)
st.caption(f"Source: csv_data/ScreenAnalysis.csv · {len(data):,} participants in the full dataset.")
