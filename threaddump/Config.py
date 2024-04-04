import yaml


class Config:
    @classmethod
    def __merge_dicts__(cls, dict1: dict | None, dict2: dict | None) -> dict:
        res = {}
        if not dict1 and not dict2:
            return res

        dict_keys = dict1.keys() if dict1 else set()
        if dict2:
            dict_keys |= dict2.keys()

        for key in dict_keys:
            if key in dict1 and isinstance(dict1[key], dict) and key in dict2 and isinstance(dict2[key], dict):
                res[key] = Config.__merge_dicts__(dict1[key], dict2[key])
            else:
                res[key] = dict2[key] if key in dict2 else dict1[key]

        return res

    def __init__(self, config_file: str):
        with open(config_file, 'r') as stream:
            self.__config = Config.__merge_dicts__({
                "debug": False,
                "files": [],
                "long_running_threads": {
                    "ignore_dummy_threads": True,
                    "threshold": 2,
                    "include_patterns": [],
                    "exclude_patterns": []
                },
                "most_recurring_threads": {
                    "ignore_dummy_threads": True,
                    "threshold": 2,
                    "include_patterns": [],
                    "exclude_patterns": []
                },
                "renderer": {
                    "type": "console"
                }
            }, yaml.safe_load(stream))

    @property
    def debug(self) -> bool:
        return self.__config["debug"]

    @property
    def files(self) -> list[str]:
        return self.__config["files"]

    @property
    def long_running_threads_ignore_dummy_threads(self) -> bool:
        return self.__config["long_running_threads"]["ignore_dummy_threads"]

    @property
    def long_running_threads_threshold(self) -> int:
        return self.__config["long_running_threads"]["threshold"]

    @property
    def long_running_threads_include_patterns(self) -> list[str]:
        return self.__config["long_running_threads"]["include_patterns"]

    @property
    def long_running_threads_exclude_patterns(self) -> list[str]:
        return self.__config["long_running_threads"]["exclude_patterns"]

    @property
    def most_recurring_threads_ignore_dummy_threads(self) -> bool:
        return self.__config["most_recurring_threads"]["ignore_dummy_threads"]

    @property
    def most_recurring_threads_threshold(self) -> int:
        return self.__config["most_recurring_threads"]["threshold"]

    @property
    def most_recurring_threads_include_patterns(self) -> list[str]:
        return self.__config["most_recurring_threads"]["include_patterns"]

    @property
    def most_recurring_threads_exclude_patterns(self) -> list[str]:
        return self.__config["long_running_threads"]["exclude_patterns"]

    @property
    def renderer_type(self) -> str:
        return self.__config["renderer"]["type"]

    @property
    def renderer_config(self) -> dict | None:
        return self.__config["renderer"]["config"] if "config" in self.__config["renderer"] else None
