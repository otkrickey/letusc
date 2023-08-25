from dataclasses import dataclass, field

from letusc.logger import Log

from .ModuleBase import ModuleBase
from .ModuleDatabase import ModuleDatabase


@dataclass
class Module(ModuleDatabase, ModuleBase):
    __logger = Log("Model.Module")

    def ___post_init___(self):
        object = self.pull()
        self.from_api(object)

    @classmethod
    def from_code(cls, code: str) -> "Module":
        try:
            code_split = code.split(":")
            if len(code_split) != 7:
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Module.from_api:InvalidData") from e
        else:
            match code_split[5]:
                case "label":
                    return LabelModule(code)
                case "page":
                    return PageModule(code)
                case "url":
                    return URLModule(code)
                case _:
                    raise ValueError("Model.Module.from_api:UnknownType")


@dataclass
class LabelModule(Module):
    __logger = Log("Model.Module.LabelModule")

    main: str = field(init=False)

    def __post_init__(self):
        object = self.pull()
        try:
            main = object["main"]
            if not isinstance(main, str):
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Module.LabelModule:InvalidData") from e
        self.from_api(object)


@dataclass
class PageModule(Module):
    __logger = Log("Model.Module.PageModule")

    title: str = field(init=False)
    module_url: str = field(init=False)

    def __post_init__(self):
        object = self.pull()
        try:
            title = object["title"]
            module_url = object["module_url"]
            if not isinstance(title, str):
                raise ValueError
            if not isinstance(module_url, str):
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Module.PageModule:InvalidData") from e
        self.from_api(object)


@dataclass
class URLModule(Module):
    __logger = Log("Model.Module.URLModule")

    title: str = field(init=False)
    module_url: str = field(init=False)

    def __post_init__(self):
        object = self.pull()
        try:
            title = object["title"]
            module_url = object["module_url"]
            if not isinstance(title, str):
                raise ValueError
            if not isinstance(module_url, str):
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Module.URLModule:InvalidData") from e
        self.from_api(object)


@dataclass
class ResourceModule(Module):
    __logger = Log("Model.Module.ResourceModule")

    title: str = field(init=False)
    module_url: str = field(init=False)
    uploaded_at: str = field(init=False)

    def __post_init__(self):
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
            raise ValueError("Model.Module.ResourceModule:InvalidData") from e
        self.from_api(object)


__all__ = [
    "Module",
    "LabelModule",
    "PageModule",
    "URLModule",
    "ResourceModule",
]
