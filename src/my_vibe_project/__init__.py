import os

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    app_name = os.getenv("APP_NAME", "MyVibeProject")
    app_env = os.getenv("APP_ENV", "development")
    print(f"Hello from {app_name}! Running in {app_env} mode.")
