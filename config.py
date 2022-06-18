# Config File

import yaml
from defs import PROJECT_PATH


# Read config.yaml
_config_dict: dict
with open(PROJECT_PATH.joinpath('config.yaml')) as config:
    _config_dict = yaml.safe_load(config)

# Parse data from config.yaml
NAME: str | None = _config_dict['name'] if 'name' in _config_dict else None
EMAIL: str | None = _config_dict['email'] if 'email' in _config_dict else None


if __name__ == '__main__':
    print('Name: ', NAME)
    print('Email: ', EMAIL)
