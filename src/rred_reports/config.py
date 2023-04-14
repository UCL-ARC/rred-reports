from pathlib import Path

from dynaconf import Dynaconf

current_dir = Path(__file__).parent

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[f"{current_dir}/settings.toml", f"{current_dir}/.secrets.toml"],
)
