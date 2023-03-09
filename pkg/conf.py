from dynaconf import Dynaconf
from pathlib import Path
from dynaconf import Dynaconf, Validator


settings = Dynaconf(
    envvar_prefix="CHAT",  # export envvars with `export CHAT_{CONFIG_NAME}={CONFIG_VALUE}`.
    settings_files=['chatgpt_voice.yaml', '.chatgpt_voice_secret.yaml'],  # Load files in the given order.
    validators=[
        Validator('OPENAI_KEY', "AZURE_KEY", "AZURE_REGION", must_exist=True),
        Validator('MAX_TOKENS', default=512, lte=4096, gte=16),
        Validator('LANGUAGE', default='en-US')
    ]
)

settings.validators.validate_all()
