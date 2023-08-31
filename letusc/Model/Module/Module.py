from dataclasses import dataclass, field

from letusc.logger import Log

from .ModuleBase import ModuleBase
from .ModuleDatabase import ModuleDatabase


@dataclass
class Module(ModuleDatabase, ModuleBase):
    __logger = Log("Model.Module")

    def ___post_init___(self):
        self.identify()
        object = self.pull()
        self.from_api(object)

    @classmethod
    def from_code(cls, code: str) -> "Module":
        __logger = Log(f"{cls.__logger}.from_code")
        try:
            code_split = code.split(":")
            if len(code_split) != 7:
                raise ValueError
        except Exception as e:
            raise ValueError(f"{__logger}:InvalidData") from e
        else:
            match code_split[5]:
                case "label":
                    return LabelModule(code)
                case "page":
                    return PageModule(code)
                case "url":
                    return URLModule(code)
                case "resource":
                    return ResourceModule(code)
                case "folder":
                    return FolderModule(code)
                case "feedback":
                    return FeedbackModule(code)
                case _:
                    raise ValueError(f"{__logger}:UnknownType")


@dataclass
class LabelModule(Module):
    __logger = Log("Model.Module.LabelModule")

    main: str = field(init=False)

    def __post_init__(self):
        self.identify()
        object = self.pull()
        try:
            main = object["main"]
            if not isinstance(main, str):
                raise ValueError
        except Exception as e:
            raise ValueError(f"{self.__logger}:InvalidData") from e
        self.from_api(object)


@dataclass
class PageModule(Module):
    __logger = Log("Model.Module.PageModule")

    title: str = field(init=False)
    module_url: str = field(init=False)

    def __post_init__(self):
        self.identify()
        object = self.pull()
        try:
            title = object["title"]
            module_url = object["module_url"]
            if not isinstance(title, str):
                raise ValueError
            if not isinstance(module_url, str):
                raise ValueError
        except Exception as e:
            raise ValueError(f"{self.__logger}:InvalidData") from e
        self.from_api(object)


@dataclass
class URLModule(Module):
    __logger = Log("Model.Module.URLModule")

    title: str = field(init=False)
    module_url: str = field(init=False)

    def __post_init__(self):
        self.identify()
        object = self.pull()
        try:
            title = object["title"]
            module_url = object["module_url"]
            if not isinstance(title, str):
                raise ValueError
            if not isinstance(module_url, str):
                raise ValueError
        except Exception as e:
            raise ValueError(f"{self.__logger}:InvalidData") from e
        self.from_api(object)


@dataclass
class ResourceModule(Module):
    __logger = Log("Model.Module.ResourceModule")

    title: str = field(init=False)
    module_url: str = field(init=False)
    uploaded_at: str = field(init=False)

    def __post_init__(self):
        self.identify()
        object = self.pull()
        try:
            title = object["title"]
            module_url = object["module_url"]
            uploaded_at = object["uploaded_at"]
            if not isinstance(title, str):
                raise ValueError
            if not isinstance(module_url, str):
                raise ValueError
            if not isinstance(uploaded_at, str):
                raise ValueError
        except Exception as e:
            raise ValueError(f"{self.__logger}:InvalidData") from e
        self.from_api(object)


@dataclass
class FolderModule(Module):
    __logger = Log("Model.Module.FolderModule")

    title: str = field(init=False)

    def __post_init__(self):
        self.identify()
        object = self.pull()
        try:
            title = object["title"]
            if not isinstance(title, str):
                raise ValueError
        except Exception as e:
            raise ValueError(f"{self.__logger}:InvalidData") from e
        self.from_api(object)


@dataclass
class FeedbackModule(Module):
    __logger = Log("Model.Module.FeedbackModule")

    title: str = field(init=False)
    module_url: str = field(init=False)
    uploaded_at: str = field(init=False)

    def __post_init__(self):
        self.identify()
        object = self.pull()
        try:
            title = object["title"]
            module_url = object["module_url"]
            # uploaded_at = object["uploaded_at"]
            if not isinstance(title, str):
                raise ValueError
            if not isinstance(module_url, str):
                raise ValueError
            # if not isinstance(uploaded_at, str):
            #     raise ValueError
        except Exception as e:
            raise ValueError(f"{self.__logger}:InvalidData") from e
        self.from_api(object)


__all__ = [
    "Module",
    "LabelModule",
    "PageModule",
    "URLModule",
    "ResourceModule",
]
