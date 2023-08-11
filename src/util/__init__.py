from os import path
from src.util.static import get_year, get_origin_url, get_auth_url, year_current
dotenv_path = path.abspath(path.join(path.dirname(__file__), '../../.env'))

year = get_year()
origin_url = get_origin_url(year)
auth_url = get_auth_url(year)
