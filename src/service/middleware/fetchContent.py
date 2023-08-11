from bs4 import BeautifulSoup
import bs4
import requests
from src.Letus.LetusPage import LetusPageV2
from src.Letus.LetusContent import LetusContentV2
from src.util.logger import Logger


def fetchContent(LP: LetusPageV2):
    __logger = Logger()
    __logger.emit('Service:Middleware:fetchContent:Start', '202', 'Fetching Page Data Start', fetchContent.__name__)
    LC = LetusContentV2(LP)

    # session = requests.Session()
    # session.cookies.update(LP.cookie)

    # response = session.get(LP.url)
    # soup = BeautifulSoup(response.text, 'html.parser')

    # title = soup.find('title')
    # if isinstance(title, bs4.Tag):
    #     LC.title = title.text

    # content = soup.find('section', {'id': 'region-main'})
    # if not isinstance(content, bs4.Tag): raise Exception('content is not Tag')

    # LC.section_data = LC.get_section_data(content)