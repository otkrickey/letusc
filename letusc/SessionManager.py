import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import letusc.model.letus as Letus
from letusc.logger import Log
from letusc.model.account import AccountBase
from letusc.URLManager import URLManager
from letusc.util import env


class SessionAutomator:
    _logger = Log("Session.Automator")

    def __init__(self, account: AccountBase):
        self.CHROME_DRIVER_PATH = env("CHROME_DRIVER_PATH")
        self.account = account

    def register(self):
        _logger = Log(f"{SessionAutomator._logger}.register")
        _logger.debug("Register to letus")

        self.service = Service(self.CHROME_DRIVER_PATH)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.login_letus()
        self.load_cookie()

    def login_letus(self):
        _logger = Log(f"{SessionAutomator._logger}.login_letus")
        _logger.debug("Login to letus (chrome)")

        auth_url = URLManager.getAuth()
        self.driver.get(auth_url)
        entry_url = "https://idp.admin.tus.ac.jp/idp/profile/SAML2/Redirect/SSO"
        WebDriverWait(self.driver, 3).until(EC.url_contains(entry_url))
        self.driver.find_element(By.NAME, "_eventId_ChooseSam2").click()
        timeout = time.time() + 60
        while True:
            origin_url = URLManager.getOrigin()
            if origin_url in self.driver.current_url:
                _logger.debug("Letus Login Success")
                break
            elif time.time() > timeout:
                _logger.error("Timeout while accessing Letus Login Page")
                raise TimeoutError(f"{_logger}:Timeout")
            elif "https://login.microsoftonline.com" in self.driver.current_url:
                while True:
                    if time.time() > timeout:
                        _logger.error("Timeout while accessing Letus Login Page")
                        raise TimeoutError(f"{_logger}:Timeout")
                    try:
                        self.login_ms()
                    except ValueError as e:
                        if (
                            str(e)
                            == f"{SessionAutomator._logger}.login_ms:PasswordError"
                        ):
                            raise e
                    except:
                        _logger.warn("Retrying...")
                        continue
                    else:
                        break
            else:
                continue

    def login_ms(self):
        _logger = Log(f"{SessionAutomator._logger}.login_ms")
        _logger.debug("Login to Microsoft")
        auth_url = URLManager.getAuth()
        self.driver.get(auth_url)

        # wait [idp.admin.tus.ac.jp]
        _logger.debug("Wait for [idp.admin.tus.ac.jp]")
        _logger.debug("Click `next` on [idp.admin.tus.ac.jp]")
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.NAME, "_eventId_ChooseSam2"))
        ).click()

        # wait [login.microsoftonline.com][email]
        _logger.debug("Wait for [login.microsoftonline.com][email]")
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        try:
            # wait [login.microsoftonline.com][email][select]
            _logger.debug("Wait for [login.microsoftonline.com][email][select]")
            _logger.debug(
                "Select `email` on [login.microsoftonline.com][email][select]"
            )
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//div[@data-test-id="{self.account.Letus.email}"]')
                )
            ).click()
        except:
            # wait [login.microsoftonline.com][email][input]
            _logger.debug("Wait for [login.microsoftonline.com][email][input]")
            _logger.debug("Input `email` on [login.microsoftonline.com][email][input]")
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, "loginfmt"))
            ).send_keys(self.account.Letus.email)
            _logger.debug("Click `next` on [login.microsoftonline.com][email][input]")
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.ID, "idSIButton9") and (By.XPATH, '//input[@value="Next"]')
                )
            ).click()

        # wait [login.microsoftonline.com][password]
        _logger.debug("Wait for [login.microsoftonline.com][password]")
        _logger.debug("Input `password` on [login.microsoftonline.com][password]")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "passwd"))
        ).send_keys(self.account.Letus.encrypted_password)
        _logger.debug("Click `sign in` on [login.microsoftonline.com][password]")
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located(
                (By.ID, "idSIButton9") and (By.XPATH, '//input[@value="Sign in"]')
            )
        ).click()

        # check [login.microsoftonline.com][password][error]
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "passwordError"))
            )
        except:
            _logger.debug("Password is Valid")
        else:
            _logger.error("Password Error")
            raise ValueError(f"{_logger}:PasswordError")

        # wait [login.microsoftonline.com][DontShowAgain]
        _logger.debug("Wait for [login.microsoftonline.com][DontShowAgain]")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "DontShowAgain"))
        ).click()
        _logger.debug("Click `yes` on [login.microsoftonline.com][DontShowAgain]")
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located(
                (By.ID, "idSIButton9") and (By.XPATH, '//input[@value="Yes"]')
            )
        ).click()
        _logger.info("Microsoft Login Success")

    def load_cookie(self):
        _logger = Log(f"{SessionAutomator._logger}.load_cookie")
        cookies = self.driver.get_cookies()
        new_cookies = []
        for new_cookie in cookies:
            if "MoodleSession" in new_cookie["name"]:
                cookie = Letus.Cookie(
                    name=new_cookie["name"],
                    value=new_cookie["value"],
                    year=new_cookie["name"].replace("MoodleSession", ""),
                )
                new_cookies.append(cookie)
                text = f'"\33[36mMoodleSession{cookie.year}\33[0m": "\33[36m{cookie.value}\33[0m"'
                _logger.info("Cookie found: {" + text + "}")
        if isinstance(self.account.Letus, Letus.LetusUserWithCookies):
            for new_cookie in new_cookies:
                for cookie in self.account.Letus.cookies:
                    if new_cookie.year == cookie.year:
                        cookie.value = new_cookie.value
                        break
                else:
                    self.account.Letus.cookies.append(new_cookie)
        else:
            self.account.Letus.cookies = new_cookies
            self.account.Letus = Letus.LetusUser.from_api(self.account.Letus.to_api())


class SessionManager(SessionAutomator):
    _logger = Log("Session.Manager")

    def login(self):
        _logger = Log(f"{SessionManager._logger}.login")
        _logger.debug("Login to letus")
        if isinstance(self.account.Letus, Letus.LetusUserWithCookies):
            for cookie in self.account.Letus.cookies:
                text = f'"\33[36m{cookie.name}\33[0m": "\33[36m{cookie.value}\33[0m"'
                _logger.info("Cookie found: {" + text + "}")
        else:
            _logger.warn("Cookie not found")
        self.register()


__all__ = [
    "SessionManager",
]
