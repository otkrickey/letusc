from .dotenv import env


year_current = 2023


def get_year():
    year = year_current
    import sys

    if "-p" in sys.argv:
        try:
            code = sys.argv[sys.argv.index("-p") + 1]
            __year = int(code.split(":")[0])
        except:
            pass
        else:
            year = __year
    if "-y" in sys.argv:
        try:
            __year = int(sys.argv[sys.argv.index("-y") + 1])
        except:
            pass
        else:
            year = __year
    return year


def get_origin_url(year=get_year(), omit_year=True):
    origin = "https://letus.ed.tus.ac.jp"
    return f"{origin}/{year}" if not omit_year else origin


def get_auth_url(year=get_year(), omit_year=True):
    return f"{get_origin_url(year, omit_year)}/auth/shibboleth/index.php"


def mongo_url():
    user = env("MONGO_USER")
    passwd = env("MONGO_PASS")
    host = env("MONGO_HOST")
    return f"mongodb+srv://{user}:{passwd}@{host}/?retryWrites=true&w=majority"
