import hashlib
import re

import bs4
import requests
from bs4 import BeautifulSoup

from letusc.logger import Log
from letusc.model.account import Account
from letusc.model.base import BaseDatabase
from letusc.model.content import Content, NewContent
from letusc.model.module import Module, NewModule
from letusc.model.page import NewPage, Page, PageDatabase


class PageParser:
    __logger = Log("PageParser")

    def __init__(self, account: Account, page_id: str):
        # prepare session information
        PageParser.__logger.info("Preparing session information")
        self.account = account
        self.page = NewPage.from_code(page_id)
        try:
            self.page_old = Page.from_code(page_id)
        except ValueError as e:
            if str(e) == f"{BaseDatabase.__logger}.pull:NotFound":
                self.page_old = None
            else:
                raise e
        else:
            self.page.accounts = self.page_old.accounts
            PageParser.__logger.info(
                f"the `accounts` will be taken over from the old page"
            )
        self.contents: dict[str, NewContent] = {}
        self.modules: dict[str, NewModule] = {}
        # if not self.account.student_id in self.page.accounts:
        #     self.page.accounts.append(self.account.student_id)
        # if not self.account.discord_id in self.page.accounts:
        #     self.page.accounts.append(self.account.discord_id)
        if not self.account.Letus.cookies:
            raise Exception(f"{PageParser.__logger}:NoCookies")
        for cookie in self.account.Letus.cookies:
            if cookie.year == self.page.year:
                self.cookie = cookie
                break
        else:
            raise Exception(f"{PageParser.__logger}:NoCookies")

    def parse(self):
        # session
        self.prepare_session()
        self.get_session()

        # page
        self.soup = BeautifulSoup(self.response, "html.parser")
        self.page.parse(self.soup)
        contents = self.soup.find_all(attrs={"data-for": "section"})
        if not isinstance(contents, bs4.ResultSet):
            raise Exception("PageParser.get_main:ContentsIsNotResultSet")
        for content_el in contents:
            if not isinstance(content_el, bs4.Tag):
                raise Exception("PageParser.get_main:ContentIsNotTag")
            content_type = "section"
            content_id = content_el.attrs["data-id"]
            code = f"{self.page.code}:{content_type}:{content_id}"
            # content = NewContent(code)
            content = NewContent.from_code(code)
            content.parse(content_el)
            content_code_hash = f"{content_type}:{content_id}:{content.hash}"
            self.page.contents.append(content_code_hash)
            self.contents.update({f"{content_type}:{content_id}": content})

            modules = content_el.find_all(attrs={"data-for": "cmitem"})
            if not isinstance(modules, bs4.ResultSet):
                raise Exception("PageParser.get_content:ModulesIsNotResultSet")
            for module_el in modules:
                if not isinstance(module_el, bs4.Tag):
                    raise Exception("PageParser.get_content:ModuleIsNotTag")
                module_types = module_el.attrs["class"]
                for module_type in (
                    [module_types]
                    if isinstance(module_types, str)
                    else module_types
                    if isinstance(module_types, list)
                    else []
                ):
                    if re.match(r"^modtype_", module_type):
                        module_type = module_type.replace("modtype_", "")
                        break
                else:
                    module_type = "<Error:NoTypeFound>"
                module_id = module_el.attrs["data-id"]
                module_code = f"{content.code}:{module_type}:{module_id}"
                module = NewModule.from_code(module_code)
                module.parse(module_el)
                module_code_hash = f"{module_type}:{module_id}:{module.hash}"
                content.modules.append(module_code_hash)
                self.modules.update({f"{module_type}:{module_id}": module})

    def prepare_session(self) -> None:
        PageParser.__logger.info("Preparing session")
        self.session = requests.Session()
        self.session.cookies.update({self.cookie.name: self.cookie.value})
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
            }
        )

    def get_session(self) -> None:
        # access to page
        PageParser.__logger.info(f"Accessing to {self.page.url}")
        try:
            response = self.session.get(self.page.url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            PageParser.__logger.error(f"An HTTP error occurred: {e}")
            match e.response.status_code:
                case 404:
                    raise Exception(f"{PageParser.__logger}:NotFound")
                case 503:
                    raise Exception(f"{PageParser.__logger}:MoodleMaintenance")
                case _:
                    raise Exception(f"{PageParser.__logger}:UnknownHTTPError")
        except requests.exceptions.RequestException as e:
            PageParser.__logger.error(f"An error occurred: {e}")
            raise Exception(f"{PageParser.__logger}:UnknownError")

        # parse page
        PageParser.__logger.info("Parsing page")
        self.response = response.text

    def compare(self) -> list[dict]:
        __logger = Log(f"{PageParser.__logger}.compare")
        if not self.page_old:
            __logger.info("No old page found")
            return []
        res = []
        nc_list = self.contents
        nm_list = self.modules
        oc_list = {}

        # # NOTE:DEBUG
        for inc, nc in enumerate(self.page.contents):
            if "1081922" in nc:
                self.page.contents[
                    inc
                ] = "section:1081922:changeddddddddddddddddddddddddddddd"
            elif "1078139" in nc:
                self.page.contents.pop(inc)
        # # NOTE:DEBUG:END
        self.page.push()

        for oc in self.page_old.contents:
            key = ":".join(oc.split(":")[:2])
            value = oc.split(":")[-1]
            oc_list.update({key: value})
        for nc in nc_list.keys():
            if nc in oc_list.keys():
                new_modules = []
                changed_modules = []
                if nc_list[nc].hash != oc_list[nc]:
                    code = f"{self.page.code}:{nc}"
                    content = {
                        "code": code,
                        "status": "changed",
                        "type": "content",
                        "new": nc_list[nc],
                        "old": Content.from_code(code),
                        "modules": [],
                    }
                    oc = Content.from_code(nc_list[nc].code)
                    om_list = {}
                    for om in oc.modules:
                        key = ":".join(om.split(":")[:2])
                        value = om.split(":")[-1]
                        om_list.update({key: value})
                    for nm in nm_list.keys():
                        if nm in om_list.keys():
                            if nm_list[nm].hash != om_list[nm]:
                                code = f"{self.page.code}:{nc}:{nm}"
                                module = {
                                    "code": code,
                                    "status": "changed",
                                    "type": "module",
                                    "new": nm_list[nm],
                                    "old": Module.from_code(code),
                                }
                                changed_modules.append(module)
                        elif nm_list[nm].content_id == nc_list[nc].content_id:
                            code = f"{self.page.code}:{nc}:{nm}"
                            module = {
                                "code": code,
                                "status": "new",
                                "type": "module",
                                "new": nm_list[nm],
                                "old": None,
                            }
                            new_modules.append(module)
                    content["modules"].extend(new_modules)
                    content["modules"].extend(changed_modules)
                    res.append(content)
            else:
                code = f"{self.page.code}:{nc}"
                content = {
                    "code": code,
                    "status": "new",
                    "type": "content",
                    "new": nc_list[nc],
                    "old": None,
                    "modules": [],
                }
                for nm in nm_list.keys():
                    if nm_list[nm].content_id == nc_list[nc].content_id:
                        code = f"{self.page.code}:{nc}:{nm}"
                        module = {
                            "code": code,
                            "status": "new",
                            "type": "module",
                            "new": nm_list[nm],
                            "old": None,
                        }
                        content["modules"].append(module)
                res.append(content)

        return res
