import hashlib
import re

import bs4
from bs4 import BeautifulSoup


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
    # return soup.get_text()


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
