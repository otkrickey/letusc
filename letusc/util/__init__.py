from os import path
from .static import get_year, get_origin_url, get_auth_url, year_current


from .dotenv import env

__all__ = ["dotenv"]

# year = get_year()
year = env("YEAR")
origin_url = get_origin_url(int(year))
auth_url = get_auth_url(int(year))
