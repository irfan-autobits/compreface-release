import json
import os
import re
def get_env(name: str, default: str = None) -> str:
    if default is None:
        return os.environ[name]
    return os.environ.get(name, '') or default


def get_env_bool(name: str, default: bool = False) -> bool:
    return Constants.str_to_bool(get_env(name, str(default)))


def get_env_split(name: str, default: str = None):
    return Constants.split(get_env(name, default))


class Constants:
    @classmethod
    def _get_constants(cls):
        names = (name for name in dir(cls)
                 if not name.startswith('_')
                 and type(getattr(cls, name)).__name__ in ('float', 'int', 'str', 'bool', 'list', 'tuple'))
        return {key: getattr(cls, key) for key in names}

    @classmethod
    def to_str(cls):
        return str(cls._get_constants())

    @classmethod
    def to_json(cls):
        return json.dumps(cls._get_constants(), indent=4)

    @staticmethod
    def str_to_bool(string: str):
        return string.lower() in ('true', '1')

    @staticmethod
    def split(arr_str):
        """
        >>> Constants.split("One")
        ['One']
        >>> Constants.split("One Two")
        ['One', 'Two']
        >>> Constants.split("One  , Two")
        ['One', 'Two']
        >>> Constants.split("One,Two")
        ['One', 'Two']
        >>> Constants.split("One, Two")
        ['One', 'Two']
        >>> Constants.split(" One Two ")
        ['One', 'Two']
        """
        return [s for s in re.split(r'[,\s]+', arr_str) if s]
