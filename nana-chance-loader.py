import requests
import yaml

from cachetools import cached, TTLCache

CONFIG_FILE_URL = "https://raw.githubusercontent.com/Moe-and-Friends/Configurations/main/nana-chance.yaml"

@cached(cache=TTLCache(maxsize=1024, ttl=600))
def load_from_github():
    raw_config = requests.get(CONFIG_FILE_URL).text
    return yaml.safe_load(raw_config)

def load(obj, env=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "obj" a single key or all keys from source
    :param obj: the settings instance
    :param env: settings current env (upper case) default='DEVELOPMENT'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all from `env`
    :param filename: Custom filename to load (useful for tests)
    :return: None
    """
    # Load data from your custom data source (file, database, memory etc)
    # use `obj.set(key, value)` or `obj.update(dict)` to load data
    # use `obj.find_file('filename.ext')` to find the file in search tree
    # Return nothing

    if key:
        obj[key] = load_from_github()[key]
    else:
        config = load_from_github()
        for key, value in config.items():
            obj[key] = value

