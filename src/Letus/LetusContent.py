import dataclasses
import datetime

from src.Letus.LetusPage import LetusPageV2

###############################################################
#
#   LetusContent V2 below
#
###############################################################


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

    def __init__(self, LP: LetusPageV2):
        self.LP = LP
        self.key = LP.key

    def export(self):
        self.document = {
            'key': self.key,
            'title': self.title,
            'hash': self.hash,
            'sections': {
                section.id: {
                    'id': section.id,
                    'title': section.title,
                    'description': section.description,
                    'hash': section.hash,
                    'modules': {
                        module.id: {
                            'id': module.id,
                            'type': module.type,
                            'link': module.link,
                            'link_alt': module.link_alt,
                            'description': module.description,
                            'hash': module.hash
                        } for module in section.modules

                    }
                } for section in self.sections
            },
            'timestamp': self.timestamp.isoformat()
        }
        return self.document

    def fromDocument(self, document: dict):
        self.document = document
        self.key = document['key']
        self.title = document['title']
        self.hash = document['hash']
        self.sections = [
            LetusContent_Section(
                id=section['id'],
                title=section['title'],
                description=section['description'],
                hash=section['hash'],
                modules=[
                    LetusContent_Module(
                        id=module['id'],
                        type=module['type'],
                        link=module['link'],
                        link_alt=module['link_alt'],
                        description=module['description'],
                        hash=module['hash']
                    ) for module in section['modules'].values()
                ]
            ) for section in document['sections'].values()
        ]
        self.timestamp = datetime.datetime.fromisoformat(document['timestamp'])
        self.sync = True


# class LetusContent:
#     def __init__(self, LP: LetusPage, LA: LetusAccount):
#         self.LetusPage = LP
#         self.LetusAccount = LA

    #     self.cookies = {}
    #     LSM = LetusSessionManager(self.LetusPage, self.LetusAccount)
    #     self.cookies[f'MoodleSession{year}'] = LSM.get_cookie()
    #     self.session = requests.session()
    #     self.session.cookies.update(self.cookies)

    # def fetch_content(self):
    #     response = self.session.get(self.LetusPage.get_url())
    #     self.response = response.text
    #     self.timestamp = datetime.datetime.now()
    #     self.soup = BeautifulSoup(self.response, 'html.parser')

    #     self.title = 'undefined'

    #     title = self.soup.find('title')
    #     if isinstance(title, Tag):
    #         self.title = title.text

    #     content = self.soup.find('section', {'id': 'region-main'})
    #     if not isinstance(content, Tag): raise Exception('content is not Tag')

    #     self.section_data = self.get_section_data(content)
    #     self.document = {
    #         'id': self.LetusPage.id,
    #         'type': self.LetusPage.type,
    #         'year': self.LetusPage.year,
    #         'title': self.title,
    #         'hash': LetusContent.hash(LetusContent.text_filter(str(content), hash=True, pretty=True, no_script=True)),
    #         'sections': self.section_data,
    #         'timestamp': self.timestamp,
    #     }

    # def get_section_data(self, content):
    #     section_data = {}
    #     section_count = 0
    #     sections = content.find_all('li', {'id': re.compile(r'^section-[0-9]+$')})
    #     for section in sections:
    #         section_id = section.get('aria-labelledby')

    #         section_title = 'undefined'
    #         section_summary = 'undefined'

    #         section_title_h3 = section.find('h3', {'id': section_id})
    #         if isinstance(section_title_h3, Tag):
    #             section_title = section_title_h3.text

    #         section_summary_div = section.find('div', {'class': 'summary'})
    #         if isinstance(section_summary_div, Tag):
    #             section_summary = LetusContent.tag_filter(section_summary_div)

    #         module_data = self.get_module_data(section)
    #         section_data[section_id] = {
    #             'id': section_id,
    #             'title': section_title,
    #             'description': section_summary,
    #             'hash': LetusContent.hash(LetusContent.text_filter(str(section), hash=True, pretty=True, no_script=True)),
    #             'modules': module_data,
    #         }
    #         section_count += 1

    #     section_data['count'] = section_count
    #     return section_data

    # def get_module_data(self, section):
    #     module_data = {}
    #     module_count = 0
    #     modules = section.find_all('li', {'id': re.compile(r'^module-[0-9]+$')})
    #     for module in modules:
    #         module_id = module.get('id')

    #         module_type = 'undefined'
    #         module_link = 'undefined'
    #         module_link_alt = 'undefined'
    #         module_description = 'undefined'

    #         module_types = module.get('class')
    #         for type in module_types:
    #             if re.match(r'^modtype_', type):
    #                 module_type = type.replace('modtype_', '')
    #                 break

    #         module_link_a = module.find('a', {'class': 'aalink'})
    #         if isinstance(module_link_a, Tag):
    #             href = module_link_a.get('href')
    #             if href is not None:
    #                 module_link = href

    #         module_link_object_type = module.find('span', {'class': 'accesshide'})
    #         if isinstance(module_link_object_type, Tag):
    #             module_link_object_type.extract()

    #         if isinstance(module_link_a, Tag):
    #             module_link_alt_span = module_link_a.find('span', {'class': 'instancename'})
    #             if isinstance(module_link_alt_span, Tag):
    #                 module_link_alt = module_link_alt_span.text

    #         module_description_div = module.find('div', {'class': 'contentafterlink'})
    #         if isinstance(module_description_div, Tag):
    #             module_description = LetusContent.tag_filter(module_description_div)

    #         module_data[module_id] = {
    #             'id': module_id,
    #             'type': module_type,
    #             'hash': LetusContent.hash(LetusContent.text_filter(str(module), hash=True, pretty=True, no_script=True)),
    #             'link': module_link,
    #             'link_alt': module_link_alt,
    #             'description': module_description,
    #         }
    #         module_count += 1

    #     module_data['count'] = module_count
    #     return module_data

    # @staticmethod
    # def tag_filter(soup: Tag):
    #     tags = ['a', 'abbr', 'acronym', 'b', 'bdo', 'big', 'br', 'button', 'cite', 'code', 'dfn', 'em', 'i', 'img', 'input', 'kbd', 'label', 'map', 'object', 'q', 'samp', 'script', 'select', 'small', 'span', 'strong', 'sub', 'sup', 'textarea', 'time', 'tt', 'var']
    #     for tag in tags:
    #         for element in soup.find_all(tag):
    #             element.unwrap()
    #     soup = BeautifulSoup(str(soup), 'html.parser')
    #     return soup.get_text(separator='\n')

    # @staticmethod
    # def text_filter(text, hash=False, pretty=False, no_script=False):
    #     if hash:
    #         soup = BeautifulSoup(text, 'html.parser')
    #         for tag in soup.find_all():
    #             remove_attrs = []
    #             for attr in tag.attrs:
    #                 if re.search(r'\b([0-9a-fA-F]{14,32}|random[0-9a-fA-F]{14,32}+_group)\b', str(tag[attr])):
    #                     remove_attrs.append(attr)
    #             for attr in remove_attrs:
    #                 del tag[attr]
    #         text = str(soup)
    #     if pretty:
    #         text = re.sub(r'\n+', '\n', text)
    #         text = re.sub(r'\n\s*', ' ', text)
    #     if no_script:
    #         soup = BeautifulSoup(text, 'html.parser')
    #         for tag in soup.find_all('script'):
    #             tag.decompose()
    #         text = str(soup)
    #     return text

    # @staticmethod
    # def hash(text):
    #     return hashlib.sha256(text.encode('utf-8')).hexdigest()
