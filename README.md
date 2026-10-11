# MyVibeProject

A Python application managed with [uv](https://docs.astral.sh/uv/).

## Setup

Install `uv`, then install the project dependencies and create your local environment file:

```sh
uv sync
cp .env.example .env
```

Edit `.env` for your machine. Keep secrets there; `.env` is excluded from Git.

## Run the command-line example

```sh
uv run my-vibe-project
```

The app reads `APP_NAME` and `APP_ENV` from `.env`. Shell environment variables take precedence over values in `.env`.

## Run the multi-page survey dashboard

```sh
uv run streamlit run src/my_vibe_project/Home.py
```

The app loads `csv_data/ScreenAnalysis.csv` and opens at <http://localhost:8501>. The home page provides participant records and a filtered CSV download. The Wellness Analysis page compares screen time, stress, and sleep quality across participant groups. The Correlations page shows screen-time relationships with sleep quality and stress, with optional age-group, gender, and occupation filters. Results are descriptive and do not establish causation.
