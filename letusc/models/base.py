import hashlib
import re
from dataclasses import dataclass, field
from types import UnionType
from typing import Callable, Union, get_args, get_origin

import bs4
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorCollection

from ..logger import L

__all__ = [
    "attr_",
    "attrs_",
    "attr_dict_",
    "type_",
    "types_",
    "type_dict_",
    "from_api_attr_",
    "from_api_attrs_",
    "from_api_attr_dict_",
    "to_api_attr_",
    "to_api_attrs_",
    "to_api_attr_dict_",
    "attrs",
    "types",
    "from_api_attrs",
    "to_api_attrs",
    "BaseModel",
    "BaseDatabase",
    "BaseParser",
]


attr_ = str
attrs_ = list[attr_]
attr_dict_ = dict[attr_, attr_]

type_ = tuple[attr_, str, type]
types_ = list[type_]
type_dict_ = dict[attr_, type_]

from_api_attr_ = tuple[attr_, type, Callable]
from_api_attrs_ = list[from_api_attr_]
from_api_attr_dict_ = dict[attr_, from_api_attr_]

to_api_attr_ = tuple[attr_, Callable]
to_api_attrs_ = list[to_api_attr_]
to_api_attr_dict_ = dict[attr_, to_api_attr_]


def attrs(attrs: attrs_ = []) -> attr_dict_:
    return {attr: attr for attr in attrs}


def types(types: types_ = []) -> type_dict_:
    return {err_key: (attr, err_key, attr_type) for attr, err_key, attr_type in types}


def from_api_attrs(api_attrs: from_api_attrs_ = []) -> from_api_attr_dict_:
    return {
        attr: (attr, attr_type, converter) for attr, attr_type, converter in api_attrs
    }


def to_api_attrs(api_attrs: to_api_attrs_ = []) -> to_api_attr_dict_:
    return {attr: (attr, converter) for attr, converter in api_attrs}


@dataclass
class BaseModel:
    _l = L()
    _attrs = attrs()
    _types = types()
    _from_api_attrs = from_api_attrs()
    _to_api_attrs = to_api_attrs()

    key: str = field(init=False)
    key_name: str = field(init=False)

    def __post_init__(self) -> None:
        self._l = L(self.__class__.__name__)
        self.key = "key"
        self.key_name = "key_name"

    def check(self) -> None:
        self._check(attrs=self._attrs, types=self._types)

    def _check(self, attrs: attr_dict_ = {}, types: type_dict_ = {}) -> None:
        _l = self._l.gm("check")
        for _attr in attrs.keys():
            try:
                if not hasattr(self, _attr):
                    _l.error(f"Attribute Error: {_attr}")
                    raise ValueError
            except Exception as e:
                _l.error(
                    f"AttributeError: {_attr} in {self.__class__.__name__}({self.key_name}={self.key})"
                )
                raise ValueError(_l.c(f"AttributeError:{_attr}")) from e
        for _attr, _err, _type in types.values():
            try:
                if get_origin(_type) is Union or get_origin(_type) is UnionType:
                    if not isinstance(getattr(self, _attr, None), get_args(_type)):
                        raise TypeError
                elif get_origin(_type) is list:
                    vs = getattr(self, _attr, None)
                    if not isinstance(vs, list):
                        raise TypeError
                    for v in vs:
                        if not isinstance(v, get_args(_type)):
                            raise TypeError
                elif get_origin(_type) is dict:
                    kvs = getattr(self, _attr, None)
                    k_type, v_type = get_args(_type)
                    if not isinstance(kvs, dict):
                        raise TypeError
                    for k, v in kvs.items():
                        if not isinstance(k, k_type):
                            raise TypeError
                        if not isinstance(v, v_type):
                            raise TypeError
                elif not isinstance(getattr(self, _attr, None), _type):
                    raise TypeError
            except Exception as e:
                _l.error(
                    f"TypeError: {_attr}={getattr(self, _attr, None)} must be {_type} in {self.__class__.__name__}({self.key_name}={self.key})"
                )
                raise ValueError(_l.c(f"TypeError:{_err}")) from e

    def from_api(self, object: dict) -> None:
        self._from_api(object, attrs=self._from_api_attrs)

    def _from_api(self, object: dict, attrs: from_api_attr_dict_ = {}) -> None:
        _l = self._l.gm("from_api")
        for _attr, _type, _converter in attrs.values():
            try:
                converted_value = _converter(object)
                if get_origin(_type) is Union or get_origin(_type) is UnionType:
                    if not isinstance(converted_value, get_args(_type)):
                        raise ValueError
                elif get_origin(_type) is list:
                    if not isinstance(converted_value, list):
                        raise ValueError
                    for v in converted_value:
                        if not isinstance(v, get_args(_type)):
                            raise ValueError
                elif get_origin(_type) is dict:
                    if not isinstance(converted_value, dict):
                        raise ValueError
                    for k, v in converted_value.items():
                        if not isinstance(k, get_args(_type)[0]):
                            raise ValueError
                        if not isinstance(v, get_args(_type)[1]):
                            raise ValueError
                elif _type is type(None):
                    if converted_value is not None:
                        raise ValueError
                elif not isinstance(converted_value, _type):
                    raise ValueError
                setattr(self, _attr, converted_value)
            except Exception as e:
                _l.error(
                    f"InvalidData: {_attr} in {self.__class__.__name__}({self.key_name}={self.key})"
                )
                raise ValueError(_l.c("InvalidData")) from e

    def to_api(self) -> dict:
        _l = self._l.gm("to_api")
        return {
            attr: converter(self) for attr, converter in self._to_api_attrs.values()
        }


@dataclass
class BaseDatabase(BaseModel):
    _l = L()
    collection: AsyncIOMotorCollection = field(init=False)

    async def push(self) -> None:
        _l = self._l.gm("push")
        ignore_ids = ["1081922", "1078139", "169670", "1802075", "1802076", "180209011"]
        for ignore_id in ignore_ids:
            if ignore_id in self.key:
                _l.warn(f"Skip: {self.key_name}={self.key} because of ignore_ids")
                return
        _l.debug(f"Push {self.key_name}={self.key}")
        try:
            await self._pull()
        except ValueError as e:
            if str(e) == self._l.gm("pull").c("NotFound"):
                return await self._register()
            raise e
        else:
            await self._update()

    async def _pull(self) -> dict:
        _l = self._l.gm("pull")
        _l.debug(f"Pull: {self.key_name}={self.key}")
        filter = {self.key_name: self.key}
        object = await self.collection.find_one(filter)
        if object is None:
            _l.error(f"NotFound: {self.key_name}={self.key}")
            raise ValueError(_l.c("NotFound"))
        return object

    async def _register(self) -> None:
        _l = self._l.gm("register")
        _l.debug(f"Register: {self.key_name}={self.key}")
        try:
            await self.collection.insert_one(self.to_api())
        except Exception as e:
            raise ValueError(_l.c("DatabaseError")) from e

    async def _update(self) -> None:
        _l = self._l.gm("update")
        _l.debug(f"Update: {self.key_name}={self.key}")
        filter = {self.key_name: self.key}
        try:
            await self.collection.update_one(
                filter, {"$set": self.to_api()}, upsert=True
            )
        except Exception as e:
            raise ValueError(_l.c("DatabaseError")) from e


@dataclass
class BaseParser(BaseDatabase, BaseModel):
    _l = L()

    def _get_title(self, tag) -> str:
        _l = self._l.gm("_get_page_title")
        if not isinstance(tag, bs4.Tag):
            raise ValueError(_l.c("NoTitleFound"))
        return tag.text.lstrip().rstrip()

    def _get_main(self, tag) -> str:
        _l = self._l.gm("_get_main")
        if not isinstance(tag, bs4.Tag):
            return ""
        for br in tag.find_all("br"):
            br.replace_with("\n")
        tags = ["div", "span"]
        for _tag in tags:
            for child in tag.find_all(_tag):
                child.replace_with(child.text)
        return "\n".join(tag.stripped_strings)

    def _get_hash(self, tag) -> str:
        _l = self._l.gm("_get_hash")
        if isinstance(tag, str):
            return self.__hash(tag)
        if not isinstance(tag, bs4.Tag):
            raise ValueError(_l.c("NoMainFound"))
        return self.__hash(self._text_filter(str(tag)))

    @staticmethod
    def _tag_filter(tag: bs4.Tag, additional_tags=None) -> str:
        tags = [
            "a",
            "abbr",
            "acronym",
            "b",
            "bdo",
            "big",
            "br",
            "button",
            "cite",
            "code",
            "dfn",
            "em",
            "i",
            "img",
            "input",
            "kbd",
            "label",
            "map",
            "object",
            "q",
            "samp",
            "script",
            "select",
            "small",
            "span",
            "strong",
            "sub",
            "sup",
            "textarea",
            "time",
            "tt",
            "var",
        ]
        if additional_tags:
            tags.extend(additional_tags)
        for _tag in tags:
            for element in tag.find_all(_tag):
                element.unwrap()
        tag = BeautifulSoup(str(tag), "html.parser")
        return tag.get_text(separator="\n")

    @staticmethod
    def _text_filter(text, hash=True, pretty=2, no_script=True):
        if hash:
            soup = BeautifulSoup(text, "html.parser")
            for tag in soup.find_all():
                remove_attrs = []
                for attr in tag.attrs:
                    if re.search(
                        r"\b([0-9a-fA-F]{14,32}|random[0-9a-fA-F]{14,32}+_group|single_button[0-9a-fA-F]{14,32})\b",
                        str(tag[attr]),
                    ):
                        remove_attrs.append(attr)
                for attr in remove_attrs:
                    del tag[attr]
            text = str(soup)
        if pretty > 0:
            text = text.lstrip().rstrip()
            text = re.sub(r"\n+", "\n", text)
        if pretty > 1:
            text = re.sub(r"\n\s*", " ", text)
        if no_script:
            soup = BeautifulSoup(text, "html.parser")
            for tag in soup.find_all("script"):
                tag.decompose()
            text = str(soup)
        return text

    @staticmethod
    def __hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
