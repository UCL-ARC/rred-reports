from pathlib import Path

from dynaconf import Dynaconf

current_dir = Path(__file__).parent

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[f"{current_dir}/settings.toml", f"{current_dir}/.secrets.toml"],
    # validators=[Validator("smtp_port", gte=5000, lte=9000), Validator("smtp_host", must_exist=True)],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
