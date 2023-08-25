import hashlib
import re

import bs4
import requests
from bs4 import BeautifulSoup

from letusc.logger import Log
from letusc.Model.Account import Account
from letusc.Model.Content import Content, NewContent
from letusc.Model.Module import NewModule
from letusc.Model.Page import NewPage, Page


class PageParser:
    __logger = Log("PageParser")

    def __init__(self, account: Account, page_id: str):
        # prepare session information
        self.__logger.info("Preparing session information")
        self.account = account
        self.page = NewPage.from_code(page_id)
        try:
            self.page_old = Page.from_code(page_id)
        except ValueError as e:
            match str(e):
                case "Model.Page.Database.pull:NotFound":
                    self.page_old = None
                case _:
                    raise e
        else:
            self.page.accounts = self.page_old.accounts
            self.__logger.info(f"the `accounts` will be taken over from the old page")
        self.contents: dict[str, NewContent] = {}
        self.modules: dict[str, NewModule] = {}
        # if not self.account.student_id in self.page.accounts:
        #     self.page.accounts.append(self.account.student_id)
        # if not self.account.discord_id in self.page.accounts:
        #     self.page.accounts.append(self.account.discord_id)
        if not self.account.Letus.cookies:
            raise Exception("PageParser.__init__:NoCookies")
        for cookie in self.account.Letus.cookies:
            if cookie.year == self.page.year:
                self.cookie = cookie
                break
        else:
            raise Exception("PageParser.__init__:NoCookies")

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
            content = NewContent(code)
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
        self.__logger.info("Preparing session")
        self.session = requests.Session()
        self.session.cookies.update({self.cookie.name: self.cookie.value})
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
            }
        )

    def get_session(self) -> None:
        # access to page
        self.__logger.info(f"Accessing to {self.page.url}")
        try:
            response = self.session.get(self.page.url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.__logger.error(f"An HTTP error occurred: {e}")
            match e.response.status_code:
                case 404:
                    raise Exception("PageParser.__init__:NotFound")
                case 503:
                    raise Exception("PageParser.__init__:MoodleMaintenance")
                case _:
                    raise Exception("PageParser.__init__:UnknownHTTPError")
        except requests.exceptions.RequestException as e:
            self.__logger.error(f"An error occurred: {e}")
            raise Exception("PageParser.__init__:UnknownError")

        # parse page
        self.__logger.info("Parsing page")
        self.response = response.text

    def compare(self) -> list[dict[str, str]]:
        if not self.page_old:
            self.__logger.info("No old page found")
            return []
        res = []
        nc_list = self.contents
        nm_list = self.modules
        oc_list = {}
        for oc in self.page_old.contents:
            key = ":".join(oc.split(":")[:2])
            value = oc.split(":")[-1]
            oc_list.update({key: value})
        for nc in nc_list.keys():
            if nc in oc_list.keys():
                if nc_list[nc].hash != oc_list[nc]:
                    code = f"{self.page.code}:{nc}"
                    # res.append({"code": code, "status": "changed"})
                    res.append(
                        {
                            "status": "changed",
                            "type": "content",
                            "object": nc_list[nc],
                        }
                    )
                    oc = Content.from_code(nc_list[nc].code)
                    om_list = {}
                    for om in oc.modules:
                        key = ":".join(om.split(":")[:2])
                        value = om.split(":")[-1]
                        om_list.update({key: value})
                    for nm in nm_list.keys():
                        if nm in om_list.keys():
                            self.__logger.debug(f"{nm_list[nm].code} <-> {om_list[nm]}")
                            if nm_list[nm].hash != om_list[nm]:
                                code = f"{self.page.code}:{nc}:{nm}"
                                # res.append({"code": code, "status": "changed"})
                                res.append(
                                    {
                                        "status": "changed",
                                        "type": "module",
                                        "object": nm_list[nm],
                                    }
                                )
                        else:
                            code = f"{self.page.code}:{nc}:{nm}"
                            # res.append({"code": code, "status": "new"})
                            res.append(
                                {
                                    "status": "new",
                                    "type": "module",
                                    "object": nm_list[nm],
                                }
                            )
            else:
                code = f"{self.page.code}:{nc}"
                # res.append({"code": code, "status": "new"})
                res.append(
                    {
                        "status": "new",
                        "type": "content",
                        "object": nc_list[nc],
                    }
                )

        return res


def tag_filter(soup, additional_tags=None) -> str | None:
    if not isinstance(soup, bs4.Tag):
        return None
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
    for tag in tags:
        for element in soup.find_all(tag):
            element.unwrap()
    soup = BeautifulSoup(str(soup), "html.parser")
    return soup.get_text(separator="\n")


def text_filter(text, hash=True, pretty=2, no_script=True):
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


def hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compare_lists(li1: list[str], li2: list[str]) -> list[dict[str, str]]:
    li1_split = [{":".join(s[:2]): s[-1]} for s in [c.split(":") for c in li1]]
    li2_split = [{":".join(s[:2]): s[-1]} for s in [c.split(":") for c in li2]]
    li2_keys = [li2_item.keys() for li2_item in li2_split]
    res = []
    for li1_item in li1_split:
        if li1_item.keys() in li2_keys:
            li2_item = li2_split[li2_keys.index(li1_item.keys())]
            if li1_item[list(li1_item.keys())[0]] != li2_item[list(li2_item.keys())[0]]:
                res.append({"id": list(li1_item.keys())[0], "status": "changed"})
        else:
            res.append({"id": list(li1_item.keys())[0], "status": "new"})
    return res
