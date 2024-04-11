import yaml
import re


class ThreadAnalysisConfig:
    def __init__(self, config: dict):
        self.__config = config

    @property
    def config(self) -> dict:
        return self.__config

    @property
    def ignore_dummy_threads(self) -> bool:
        if "ignore_dummy_threads" not in self.__config:
            return True

        return bool(self.__config["ignore_dummy_threads"])

    @property
    def thread_name_include_patterns(self) -> list[re.Pattern]:
        return self.__get_patterns__("include_patterns", "thread_name")

    @property
    def thread_name_exclude_patterns(self) -> list[re.Pattern]:
        return self.__get_patterns__("exclude_patterns", "thread_name")

    @property
    def stack_trace_include_patterns(self) -> list[re.Pattern]:
        return self.__get_patterns__("include_patterns", "stack_trace")

    @property
    def stack_trace_exclude_patterns(self) -> list[re.Pattern]:
        return self.__get_patterns__("exclude_patterns", "stack_trace")

    def __get_patterns__(self, key: str, subkey: str) -> list[re.Pattern]:
        if key not in self.__config or subkey not in self.__config[key]:
            return []

        return [re.compile(pattern, re.MULTILINE) for pattern in self.__config[key][subkey]]


class LongRunningThreadsConfig(ThreadAnalysisConfig):
    def __init__(self, config: dict):
        super().__init__(config)

    @property
    def threshold(self) -> int:
        return self.config["threshold"]


class MostRecurringThreadsConfig(ThreadAnalysisConfig):
    def __init__(self, config: dict):
        super().__init__(config)

    @property
    def threshold(self) -> int:
        return self.config["threshold"]


class RendererConfig:
    def __init__(self, config: dict):
        self.__config = config

    @property
    def type(self) -> str:
        return self.__config["type"]

    @property
    def config(self) -> dict | None:
        return self.__config["config"] if "config" in self.__config else None


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
                    "include_patterns": {
                        "thread_name": [],
                        "stack_trace": []
                    },
                    "exclude_patterns": {
                        "thread_name": [],
                        "stack_trace": []
                    }
                },
                "most_recurring_threads": {
                    "ignore_dummy_threads": True,
                    "threshold": 2,
                    "include_patterns": {
                        "thread_name": [],
                        "stack_trace": []
                    },
                    "exclude_patterns": {
                        "thread_name": [],
                        "stack_trace": []
                    }
                },
                "renderer": {
                    "type": "console"
                }
            }, yaml.safe_load(stream))

            self.__long_running_threads = LongRunningThreadsConfig(self.__config["long_running_threads"])
            self.__most_recurring_threads = MostRecurringThreadsConfig(self.__config["most_recurring_threads"])
            self.__renderer = RendererConfig(self.__config["renderer"])

    @property
    def debug(self) -> bool:
        return self.__config["debug"]

    @property
    def files(self) -> list[str]:
        return self.__config["files"]

    @property
    def long_running_threads(self) -> LongRunningThreadsConfig:
        return self.__long_running_threads

    @property
    def most_recurring_threads(self) -> MostRecurringThreadsConfig:
        return self.__most_recurring_threads

    @property
    def renderer(self) -> RendererConfig:
        return self.__renderer
