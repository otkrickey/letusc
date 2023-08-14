import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.Letus.LetusAccount import LetusAccount
from src.util import auth_url, dotenv_path, origin_url
from src.util.logger import Log


class LetusSessionController:
    def __init__(self):
        load_dotenv(verbose=True)
        self.__dotenv_path = dotenv_path
        load_dotenv(self.__dotenv_path)

        # get environment variables
        CHROME_DRIVER_PATH = os.environ.get("CHROME_DRIVER_PATH")
        if CHROME_DRIVER_PATH is None:
            raise ValueError("CHROME_DRIVER_PATH is not set")
        else:
            self.CHROME_DRIVER_PATH = CHROME_DRIVER_PATH

    def login(self, LA: LetusAccount):
        __logger = Log("Controller.LSC.login")
        __logger.debug("Login to letus")

        for key in LA.cookie.keys():
            if key == f"MoodleSession{LA.year}":
                cookie = LA.cookie[key]
                text = f'"\33[36m{key}\33[0m": "\33[36m{cookie}\33[0m"'
                __logger.info("Cookie found: {" + text + "}")
                break
        else:
            __logger.warn("Cookie not found")
        self.register(LA)

    def register(self, LA: LetusAccount):
        __logger = Log("Controller.LSC.register")
        __logger.debug("Register to letus")
        self.service = Service(self.CHROME_DRIVER_PATH)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.__login_letus(LA)
        self.load_cookie(LA)

    def __login_letus(self, LA: LetusAccount):
        __logger = Log("Controller.LSC.__login_letus")
        __logger.debug("Login to letus (chrome)")
        self.driver.get(auth_url)
        entry_url = "https://idp.admin.tus.ac.jp/idp/profile/SAML2/Redirect/SSO"
        WebDriverWait(self.driver, 3).until(EC.url_contains(entry_url))
        self.driver.find_element(By.NAME, "_eventId_ChooseSam2").click()
        timeout = time.time() + 60
        # timeout = time.time() + 10
        while True:
            if origin_url in self.driver.current_url:
                __logger.debug("Letus Login Success")
                break
            elif time.time() > timeout:
                __logger.error("Timeout while accessing Letus Login Page")
                raise TimeoutError("LetusSessionController:login:__login_letus:Timeout")
            elif "https://login.microsoftonline.com" in self.driver.current_url:
                while True:
                    if time.time() > timeout:
                        __logger.error("Timeout while accessing Letus Login Page")
                        raise TimeoutError(
                            "LetusSessionController:login:__login_letus:Timeout"
                        )
                    try:
                        self.__login_ms(LA)
                    except ValueError as e:
                        match str(e):
                            case "LetusSessionController:login:__login_ms:PasswordError":
                                raise e
                    except:
                        __logger.warn("Retrying...")
                        continue
                    else:
                        break
            else:
                continue

    def __login_ms(self, LA: LetusAccount):
        __logger = Log("Controller.LSC.__login_ms")
        __logger.debug("Login to Microsoft")
        self.driver.get(auth_url)

        # wait [idp.admin.tus.ac.jp]
        __logger.debug("Wait for [idp.admin.tus.ac.jp]")
        __logger.debug("Click `next` on [idp.admin.tus.ac.jp]")
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.NAME, "_eventId_ChooseSam2"))
        ).click()

        # wait [login.microsoftonline.com][email]
        __logger.debug("Wait for [login.microsoftonline.com][email]")
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        try:
            # wait [login.microsoftonline.com][email][select]
            __logger.debug("Wait for [login.microsoftonline.com][email][select]")
            __logger.debug(
                "Select `email` on [login.microsoftonline.com][email][select]"
            )
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//div[@data-test-id="{LA.email}"]')
                )
            ).click()
        except:
            # wait [login.microsoftonline.com][email][input]
            __logger.debug("Wait for [login.microsoftonline.com][email][input]")
            __logger.debug("Input `email` on [login.microsoftonline.com][email][input]")
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, "loginfmt"))
            ).send_keys(LA.email)
            __logger.debug("Click `next` on [login.microsoftonline.com][email][input]")
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.ID, "idSIButton9") and (By.XPATH, '//input[@value="Next"]')
                )
            ).click()

        # wait [login.microsoftonline.com][password]
        __logger.debug("Wait for [login.microsoftonline.com][password]")
        __logger.debug("Input `password` on [login.microsoftonline.com][password]")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "passwd"))
        ).send_keys(LA.encrypted_password)
        __logger.debug("Click `sign in` on [login.microsoftonline.com][password]")
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
            __logger.debug("Password is Valid")
        else:
            __logger.error("Password Error")
            raise ValueError("LetusSessionController:login:__login_ms:PasswordError")

        # wait [login.microsoftonline.com][DontShowAgain]
        __logger.debug("Wait for [login.microsoftonline.com][DontShowAgain]")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "DontShowAgain"))
        ).click()
        __logger.debug("Click `yes` on [login.microsoftonline.com][DontShowAgain]")
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located(
                (By.ID, "idSIButton9") and (By.XPATH, '//input[@value="Yes"]')
            )
        ).click()
        __logger.info("Microsoft Login Success")

    def load_cookie(self, LA: LetusAccount):
        __logger = Log("Controller.LSC.load_cookie")
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            if cookie["name"] == f"MoodleSession{LA.year}":
                self.__new_cookie = cookie["value"]
                text = f'"\33[36mMoodleSession{LA.year}\33[0m": "\33[36m{self.__new_cookie}\33[0m"'
                __logger.info("Cookie found: {" + text + "}")
                break

        if self.__new_cookie and isinstance(self.__new_cookie, str):
            LA.cookie[f"MoodleSession{LA.year}"] = self.__new_cookie
            __logger.info("Cookie found")
