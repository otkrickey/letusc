import dataclasses
import datetime

from src.Letus.v2.LetusPage import LetusPage

# model_template = {
#     "id": "number",
#     "type": "course|else",
#     "year": "number",
#     "semester": "number",
#     "title": "string",
#     "hash": "hash()",
#     "sections": {
#         "count": "number",
#         "sectionid-{id}-title": {
#             "id": "number",
#             "title": "string",
#             "hash": "hash()",
#             "modules": {
#                 "count": "number",
#                 "module-{id}": {
#                     "id": "number",
#                     "type": "resource|url|label|else",
#                     "hash": "hash()",
#                     "link": "string|undefined",
#                     "link_alt": "string|undefined",
#                     "description": "string|undefined"
#                 }
#             }
#         }
#     },
#     "timestamp": "timestamp()"
# }


@dataclasses.dataclass
class LetusContent_Module:
    id: str
    type: str | None
    link: str | None
    link_alt: str | None
    description: str | None
    hash: str


@dataclasses.dataclass
class LetusContent_Section:
    id: str
    title: str | None
    description: str | None
    hash: str
    modules: list[LetusContent_Module]


class LetusContentV2:
    key: str
    title: str
    hash: str
    sections: list[LetusContent_Section]
    timestamp: datetime.datetime

    document: dict

    sync = False

    def __init__(self, LP: LetusPage):
        self.LP = LP
        self.key = LP.key

    def export(self):
        self.document = {
            "key": self.key,
            "title": self.title,
            "hash": self.hash,
            "sections": {
                section.id: {
                    "id": section.id,
                    "title": section.title,
                    "description": section.description,
                    "hash": section.hash,
                    "modules": {
                        module.id: {
                            "id": module.id,
                            "type": module.type,
                            "link": module.link,
                            "link_alt": module.link_alt,
                            "description": module.description,
                            "hash": module.hash,
                        }
                        for module in section.modules
                    },
                }
                for section in self.sections
            },
            "timestamp": self.timestamp.isoformat(),
        }
        return self.document

    def fromDocument(self, document: dict):
        self.document = document
        self.key = document["key"]
        self.title = document["title"]
        self.hash = document["hash"]
        self.sections = [
            LetusContent_Section(
                id=section["id"],
                title=section["title"],
                description=section["description"],
                hash=section["hash"],
                modules=[
                    LetusContent_Module(
                        id=module["id"],
                        type=module["type"],
                        link=module["link"],
                        link_alt=module["link_alt"],
                        description=module["description"],
                        hash=module["hash"],
                    )
                    for module in section["modules"].values()
                ],
            )
            for section in document["sections"].values()
        ]
        self.timestamp = datetime.datetime.fromisoformat(document["timestamp"])
        self.sync = True
