import datetime
import hashlib
import re

import bs4
import pymongo
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import WriteError

from src.Letus.v2.LetusContent import (
    LetusContent_Module,
    LetusContent_Section,
    LetusContentV2,
)
from src.util.logger import Logger


class ContentManagerV2:
    changed = False

    def __init__(self, LC: LetusContentV2):
        self.LC = LC
        self.client = MongoClient(
            "mongodb+srv://otkrickey:Tm6Mp291LJwFIscK@letus.tcigkrt.mongodb.net/?retryWrites=true&w=majority"
        )
        self.db = self.client["letus"]
        self.collection = self.db["courses"]

        self.__logger = Logger(self.__class__.__name__)

        self.CH = ContentHandlerV2(self.LC)
        self.LCp = LetusContentV2(self.LC.LP)

    def check(self):
        self.__logger.emit(
            "ContentManager:check:Start",
            "202",
            "Checking content info",
            self.check.__name__,
        )
        try:
            if not self.LC.sync and not self.LCp.sync:
                self.__logger.emit(
                    "ContentManager:check:SyncError",
                    "202",
                    "Sync disabled",
                    self.check.__name__,
                )
                raise ValueError("ContentManager:check:SyncError")
        except ValueError:
            self.pull()
            return self.check()
        else:
            self.__logger.emit(
                "ContentManager:check:Success",
                "200",
                "Content info checked",
                self.check.__name__,
            )
            return

    def pull(self):
        self.__logger.emit(
            "ContentManager:pull:Start",
            "202",
            "Pulling content info",
            self.pull.__name__,
        )
        filter = {"key": self.LC.LP.key}
        content = self.collection.find_one(
            filter, sort=[("timestamp", pymongo.DESCENDING)]
        )
        try:
            if content is None:
                self.__logger.emit(
                    "ContentManager:pull:NoPrevious",
                    "202",
                    "No previous content found",
                    self.pull.__name__,
                )
                raise ValueError("ContentManager:pull:NoPrevious")
            self.LCp = LetusContentV2(self.LC.LP)
            self.LCp.fromDocument(content)
        except ValueError as e:
            if "ContentManager:pull:NoPrevious" in str(e):
                self.changed = True
                self.LC.sync = True
        except KeyError:
            self.__logger.emit(
                "ContentManager:pull:KeyError", "202", "KeyError", self.pull.__name__
            )
            raise KeyError("ContentManager:pull:KeyError")
        else:
            if self.LC.hash != self.LCp.hash:
                self.__logger.emit(
                    "ContentManager:pull:HashChanged",
                    "202",
                    "Hash changed",
                    self.pull.__name__,
                )
                self.changed = True
            self.LCp.sync = True
            self.__logger.emit(
                "ContentManager:pull:Success",
                "200",
                "Content info pulled",
                self.pull.__name__,
            )
            return

    def push(self):
        self.__logger.emit(
            "ContentManager:push:Start",
            "202",
            "Pushing content info",
            self.push.__name__,
        )
        try:
            self.check()
        except ValueError:
            self.__logger.emit(
                "ContentManager:push:ValueError",
                "202",
                "ValueError",
                self.push.__name__,
            )
            raise ValueError("ContentManager:push:ValueError")
        else:
            if self.changed:
                self.register()

    def register(self):
        self.__logger.emit(
            "ContentManager:register:Start",
            "202",
            "Registering content info",
            self.register.__name__,
        )
        LCO = self.LC.export()
        try:
            self.__logger.emit(
                "ContentManager:register:Creating",
                "202",
                "Creating content info",
                self.register.__name__,
            )
            self.collection.insert_one(LCO)
        except WriteError:
            self.__logger.emit(
                "ContentManager:register:WriteError",
                "202",
                "WriteError",
                self.register.__name__,
            )
            raise ValueError("ContentManager:register:WriteError")
        else:
            self.__logger.emit(
                "ContentManager:register:Success",
                "200",
                "Content info registered",
                self.register.__name__,
            )
            return


class ContentHandlerV2:
    def __init__(self, LC: LetusContentV2):
        self.LC = LC
        self.client = MongoClient("localhost", 27017)
        self.db = self.client["letus"]
        self.collection = self.db["courses"]

        self.session = requests.Session()
        self.session.cookies.update(self.LC.LP.cookie)
        response = self.session.get(self.LC.LP.url)
        self.response = response.text
        self.soup = BeautifulSoup(self.response, "html.parser")

        self.LC.timestamp = datetime.datetime.now()

        self.get_content()

    def get_content(self):
        # title
        title = self.soup.find("title")
        if isinstance(title, bs4.Tag):
            self.LC.title = title.text
        # main
        content = self.soup.find("section", {"id": "region-main"})
        if not isinstance(content, bs4.Tag):
            raise Exception("content is not Tag")
        sections = content.find_all("li", {"id": re.compile(r"^section-[0-9]+$")})
        if not isinstance(sections, bs4.ResultSet):
            raise Exception("sections is not ResultSet")
        self.LC.hash = ContentHandlerV2.hash(
            ContentHandlerV2.text_filter(
                str(content), hash=True, pretty=True, no_script=True
            )
        )
        # print(ContentHandlerV2.text_filter(str(content), hash=True, pretty=True, no_script=True))
        LC_Sections = [
            self.get_section(section)
            for section in sections
            if isinstance(section, bs4.Tag)
        ]
        self.LC.sections = LC_Sections

    def get_section(self, section: bs4.Tag) -> LetusContent_Section:
        id = section.get("aria-labelledby")
        title_h3 = section.find("h3", {"id": id})
        title = title_h3.text if isinstance(title_h3, bs4.Tag) else None

        summary_div = section.find("div", {"class": "summary"})
        summary = (
            ContentHandlerV2.tag_filter(summary_div)
            if isinstance(summary_div, bs4.Tag)
            else None
        )
        hash = ContentHandlerV2.hash(
            ContentHandlerV2.text_filter(
                str(section), hash=True, pretty=True, no_script=True
            )
        )

        modules = section.find_all("li", {"id": re.compile(r"^module-[0-9]+$")})
        if not isinstance(modules, bs4.ResultSet):
            raise Exception("modules is not ResultSet")

        LC_Modules = [
            self.get_module(module) for module in modules if isinstance(module, bs4.Tag)
        ]

        return LetusContent_Section(str(id), title, summary, hash, LC_Modules)

    def get_module(self, module: bs4.Tag) -> LetusContent_Module:
        id = str(module.get("id"))
        type = None
        link = None
        # get module type
        types = module.get("class")
        for _type in (
            [types]
            if isinstance(types, str)
            else types
            if isinstance(types, list)
            else []
        ):
            if re.match(r"^modtype_", _type):
                type = _type.replace("modtype_", "")
                break

        # get module link
        link_a = module.find("a", {"class": "aalink"})
        link_a_href = link_a.get("href") if isinstance(link_a, bs4.Tag) else None
        if link_a_href:
            link = str(link_a_href)

        # remove invisible elements
        link_object_type = module.find("span", {"class": "accesshide"})
        if isinstance(link_object_type, bs4.Tag):
            link_object_type.extract()

        # get module link alt
        link_alt_span = (
            module.find("span", {"class": "instancename"})
            if not isinstance(link_a, bs4.Tag)
            else None
        )
        link_alt = link_alt_span.text if isinstance(link_alt_span, bs4.Tag) else None

        # get module description
        description_div = module.find("div", {"class": "contentafterlink"})
        description = (
            ContentHandlerV2.tag_filter(description_div)
            if isinstance(description_div, bs4.Tag)
            else None
        )

        hash = ContentHandlerV2.hash(
            ContentHandlerV2.text_filter(
                str(module), hash=True, pretty=True, no_script=True
            )
        )

        return LetusContent_Module(id, type, link, link_alt, description, hash)

    @staticmethod
    def tag_filter(soup: bs4.Tag):
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
        for tag in tags:
            for element in soup.find_all(tag):
                element.unwrap()
        soup = BeautifulSoup(str(soup), "html.parser")
        return soup.get_text(separator="\n")

    @staticmethod
    def text_filter(text, hash=False, pretty=False, no_script=False):
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
        if pretty:
            text = re.sub(r"\n+", "\n", text)
            text = re.sub(r"\n\s*", " ", text)
        if no_script:
            soup = BeautifulSoup(text, "html.parser")
            for tag in soup.find_all("script"):
                tag.decompose()
            text = str(soup)
        return text

    @staticmethod
    def hash(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


# class ContentManager:
#     def __init__(self, LC: LetusContent):
#         self.LetusContent = LC
#         self.client = MongoClient('mongodb+srv://otkrickey:Tm6Mp291LJwFIscK@letus.tcigkrt.mongodb.net/?retryWrites=true&w=majority')
#         self.db = self.client['letus']
#         self.collection = self.db['courses']

#         # self.LetusContent.fetch_content()
#         # self.document = self.LetusContent.document
#         self.document = {}

#         self.__logger = Logger(self.__class__.__name__)

#     def upload(self):
#         self.collection.insert_one(self.document)
#         self.__logger.info(f'uploaded document: {self.document["id"]} (hash: {self.document["hash"]})', self.upload.__name__)

#     def get_previous(self):
#         filter = {
#             'type': self.LetusContent.LetusPage.type,
#             'year': self.LetusContent.LetusPage.year,
#             'id': self.LetusContent.LetusPage.id,
#         }
#         return self.collection.find_one(filter, sort=[('timestamp', pymongo.DESCENDING)])

#     def check_content_changes(self):
#         previous = self.get_previous()
#         changed = False
#         if previous is None:
#             self.__logger.info('No previous document found', self.check_content_changes.__name__)
#             changed = True
#             return changed
#         if previous['hash'] != self.document['hash']:
#             self.__logger.info(f'content hash changed: {previous["hash"]} -> {self.document["hash"]}', self.check_content_changes.__name__)
#             changed = self.check_section_changes(previous['sections'], self.document['sections'])

#         if not changed:
#             self.__logger.info('no changes found', self.check_content_changes.__name__)
#         return changed

#     def check_section_changes(self, previous, current):
#         if previous['count'] != current['count']:
#             self.__logger.info(f'section count changed: {previous["count"]} -> {current["count"]}', self.check_section_changes.__name__)

#         changed = False
#         previous_section_keys = list(previous.keys())
#         previous_section_keys.remove('count')
#         current_section_keys = list(current.keys())
#         current_section_keys.remove('count')
#         common_section_keys = set(previous_section_keys).intersection(current_section_keys)

#         for key in previous_section_keys:
#             if key not in current_section_keys:
#                 self.__logger.info(f'section removed: {key} (hash: {previous[key]["hash"]})', self.check_section_changes.__name__)
#                 changed = True
#         for key in current_section_keys:
#             if key not in previous_section_keys:
#                 self.__logger.info(f'section added: {key} (hash: {current[key]["hash"]})', self.check_section_changes.__name__)
#                 changed = True
#         for key in common_section_keys:
#             if previous[key]['hash'] != current[key]['hash']:
#                 self.__logger.info(f'section hash changed: {key} (hash: {previous[key]["hash"]} -> {current[key]["hash"]})', self.check_section_changes.__name__)
#                 changed = self.check_module_changes(previous[key]['modules'], current[key]['modules'])
#         return changed

#     def check_module_changes(self, previous, current):
#         if previous['count'] != current['count']:
#             self.__logger.info(f'module count changed: {previous["count"]} -> {current["count"]}', self.check_module_changes.__name__)

#         changed = False
#         previous_module_keys = list(previous.keys())
#         previous_module_keys.remove('count')
#         current_module_keys = list(current.keys())
#         current_module_keys.remove('count')
#         common_module_keys = set(previous_module_keys).intersection(current_module_keys)

#         for key in previous_module_keys:
#             if key not in current_module_keys:
#                 self.__logger.info(f'module removed: {key} (hash: {previous[key]["hash"]})', self.check_module_changes.__name__)
#                 changed = True
#         for key in current_module_keys:
#             if key not in previous_module_keys:
#                 self.__logger.info(f'module added: {key} (hash: {current[key]["hash"]})', self.check_module_changes.__name__)
#                 changed = True
#         for key in common_module_keys:
#             if previous[key]['hash'] != current[key]['hash']:
#                 self.__logger.info(f'module hash changed: {key} (hash: {previous[key]["hash"]} -> {current[key]["hash"]})', self.check_module_changes.__name__)
#                 changed = True
#         return changed
