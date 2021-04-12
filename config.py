
from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    environments=False,
    envvar_prefix="CHANCE",
    env_switcher="CHANCE_ENV",
    fresh_vars=[
        'COMRADE_ROLE_IDS',
        'INTERVALS',
        'LETHAL_ROLE_IDS',
        'TRIGGERS',
        'NANA_COMRADE_SAFE_MESSAGE',
        'NANA_COMRADE_LETHAL_MESSAGE',
        'NANA_CAPITALIST_SAFE_MESSAGE',
        'NANA_CAPITALIST_LETHAL_MESSAGE',
    ],
    loaders=['nana-chance-loader'],
    load_dotenv=False,
    redis_enabled=False,
    settings_files=['settings.toml', '.settings.toml', '.secrets.toml'],
    vault_enabled=False,
    validators=[
        Validator('COMRADE_ROLE_IDS', is_type_of=list, must_exist=True),
        Validator('DISCORD_GUILD_IDS', is_type_of=list, must_exist=True),
        Validator('DISCORD_TOKEN', is_type_of=str, must_exist=True),
        Validator('INTERVALS', is_type_of=list, must_exist=True),
        Validator('LETHAL_ROLE_IDS', is_type_of=list),
        Validator('TRIGGERS', is_type_of=list),
        Validator('NANA_COMRADE_SAFE_MESSAGE', is_type_of=str, must_exist=True),
        Validator('NANA_COMRADE_LETHAL_MESSAGE', is_type_of=str, must_exist=True),
        Validator('NANA_CAPITALIST_SAFE_MESSAGE', is_type_of=str, must_exist=True),
        Validator('NANA_CAPITALIST_LETHAL_MESSAGE', is_type_of=str, must_exist=True),
    ]
)
