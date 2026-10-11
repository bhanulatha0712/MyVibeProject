import altair as alt
import streamlit as st

from my_vibe_project.survey_data import APP_NAME, add_sidebar_filters, apply_styles

st.set_page_config(page_title=f"{APP_NAME} | Wellness Analysis", layout="wide")
apply_styles()
_, filtered, selected = add_sidebar_filters("overview")

st.caption("SURVEY DASHBOARD  /  PARTICIPANT WELLNESS")
st.title("Wellness Analysis")
st.write(
    "Choose participant criteria in the sidebar to see how daily screen use, stress, "
    "and self-reported sleep quality differ across the matching groups."
)
st.caption(
    "These are observational survey results. Differences and associations do not establish "
    "causation or provide clinical assessments."
)

if filtered.empty:
    st.warning("No participants match these criteria. Change one or more sidebar selections.")
    st.stop()

comparison_options = []
group_columns = {}
if selected["age_group"] == "All ages":
    comparison_options.append("Age group")
    group_columns["Age group"] = "age_group"
if selected["gender"] == "All genders":
    comparison_options.append("Gender")
    group_columns["Gender"] = "gender"
if selected["occupation"] == "All occupations":
    comparison_options.append("Occupation")
    group_columns["Occupation"] = "occupation"

metric_columns = st.columns(4)
metric_columns[0].metric("Participants", f"{len(filtered):,}")
metric_columns[1].metric("Mean screen time", f"{filtered['screen_time_hours'].mean():.1f} h/day")
metric_columns[2].metric("Mean stress", f"{filtered['stress_level_0_10'].mean():.1f} / 10")
metric_columns[3].metric("Mean sleep quality", f"{filtered['sleep_quality_1_5'].mean():.1f} / 5")

st.subheader("Compare participant groups")
if comparison_options:
    compare_by = st.selectbox("Break down results by", comparison_options)
    group_column = group_columns[compare_by]
    grouped = (
        filtered.groupby(group_column, as_index=False, observed=True)
        .agg(
            participants=("user_id", "size"),
            screen_time=("screen_time_hours", "mean"),
            stress=("stress_level_0_10", "mean"),
            sleep_quality=("sleep_quality_1_5", "mean"),
        )
        .sort_values(group_column)
    )
    st.caption(
        f"Averages for {len(filtered):,} matching participants, compared across "
        f"{compare_by.lower()} groups."
    )
else:
    compare_by = "Selected participants"
    group_column = "comparison_group"
    grouped = filtered.assign(comparison_group="Selected group").groupby(
        group_column, as_index=False
    ).agg(
        participants=("user_id", "size"),
        screen_time=("screen_time_hours", "mean"),
        stress=("stress_level_0_10", "mean"),
        sleep_quality=("sleep_quality_1_5", "mean"),
    )
    st.caption("All three criteria are specific, so the charts summarize this selected group.")

st.caption("Hover for exact values. Click a bar to highlight a group; click again to clear.")
chart_specs = [
    ("screen_time", "Average screen time", "Hours per day", "#44C5A2", ".1f"),
    ("stress", "Average stress", "Scale of 0–10", "#F09A72", ".1f"),
    ("sleep_quality", "Average sleep quality", "Scale of 1–5", "#79B8E5", ".2f"),
]
for measure, title, axis_label, color, number_format in chart_specs:
    st.markdown(f"**{title}**")
    selected_group = alt.selection_point(fields=[group_column], on="click", empty="all")
    hovered_group = alt.selection_point(fields=[group_column], on="pointerover", clear="pointerout")
    bars = (
        alt.Chart(grouped)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=38)
        .encode(
            x=alt.X(
                f"{group_column}:N",
                title=compare_by,
                sort=None,
                axis=alt.Axis(labelAngle=-25, labelLimit=140),
            ),
            y=alt.Y(f"{measure}:Q", title=axis_label, scale=alt.Scale(zero=True)),
            color=alt.condition(selected_group, alt.value(color), alt.value("#29374D")),
            opacity=alt.condition(hovered_group, alt.value(1), alt.value(0.82)),
            tooltip=[
                alt.Tooltip(f"{group_column}:N", title=compare_by),
                alt.Tooltip("participants:Q", title="Participants", format=","),
                alt.Tooltip(f"{measure}:Q", title=axis_label, format=number_format),
            ],
        )
        .add_params(selected_group, hovered_group)
        .properties(height=300, background="#0E1525")
        .configure_view(stroke="transparent")
        .configure_axis(
            labelColor="#A7B5C7",
            titleColor="#A7B5C7",
            gridColor="#29374D",
            domainColor="#526176",
            tickColor="#526176",
        )
    )
    st.altair_chart(bars, use_container_width=True)

st.subheader("Group summary")
summary = grouped.rename(
    columns={
        group_column: compare_by,
        "participants": "Participants",
        "screen_time": "Mean screen time (h/day)",
        "stress": "Mean stress (0-10)",
        "sleep_quality": "Mean sleep quality (1-5)",
    }
)
st.dataframe(summary.round(2), hide_index=True, use_container_width=True)
