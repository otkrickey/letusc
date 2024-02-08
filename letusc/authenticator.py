import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .logger import get_logger
from .models.account import AccountBase
from .models.cookie import Cookie
from .models.event import Progress
from .models.letus import LetusUser, LetusUserWithCookies
from .sockets import SocketIOClient
from .task import TaskManager
from .url import URLManager
from .util import env

logger = get_logger(__name__)

__all__ = [
    "Authenticator",
]


class AuthController:
    def __init__(self, account: AccountBase, socket_client_id: str = ""):
        self.CHROME_DRIVER_PATH = env("CHROME_DRIVER_PATH")
        self.account = account
        self.use_socket_io = socket_client_id != ""
        self.sid = socket_client_id
        self.loop = TaskManager().get_loop()
        if self.use_socket_io:
            self.sio_client = SocketIOClient.instance()

    def _register(self):
        logger.debug("Register to letus")
        if self.use_socket_io:
            progress = Progress(self.sid, "register_to_letus", "start", 1)
            self.loop.create_task(self.sio_client.send_progress(progress))

        self.service = Service(self.CHROME_DRIVER_PATH)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self._login_letus()
        self._load_cookie()

    def _login_letus(self):
        logger.debug("Login to letus (chrome)")
        if self.use_socket_io:
            progress = Progress(self.sid, "login_to_letus", "start", 1)
            self.loop.create_task(self.sio_client.send_progress(progress))

        auth_url = URLManager.getAuth()
        self.driver.get(auth_url)
        entry_url = "https://idp.admin.tus.ac.jp/idp/profile/SAML2/Redirect/SSO"
        WebDriverWait(self.driver, 3).until(EC.url_contains(entry_url))
        self.driver.find_element(By.NAME, "_eventId_ChooseSam2").click()
        timeout = time.time() + 60
        while True:
            origin_url = URLManager.getOrigin()
            if origin_url in self.driver.current_url:
                logger.debug("Letus Login Success")
                break
            elif time.time() > timeout:
                logger.error("Timeout while accessing Letus Login Page")
                raise TimeoutError(logger.c("Timeout"))
            elif "https://login.microsoftonline.com" in self.driver.current_url:
                while True:
                    if time.time() > timeout:
                        logger.error("Timeout while accessing Letus Login Page")
                        raise TimeoutError(logger.c("Timeout"))
                    try:
                        self._login_ms()
                    except ValueError as e:
                        if str(e) == f"AuthController._login_ms:PasswordError":
                            raise e
                    except:
                        logger.warn("Retrying...")
                        continue
                    else:
                        break
            else:
                continue

    def _login_ms(self):
        logger.debug("Login to Microsoft")
        auth_url = URLManager.getAuth()
        self.driver.get(auth_url)

        # NOTE:wait [idp.admin.tus.ac.jp]
        logger.debug("Wait for [idp.admin.tus.ac.jp]")
        logger.debug("Click `next` on [idp.admin.tus.ac.jp]")
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.NAME, "_eventId_ChooseSam2"))
        ).click()

        # NOTE:wait [login.microsoftonline.com][email]
        logger.debug("Wait for [login.microsoftonline.com][email]")
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        try:
            # NOTE:wait [login.microsoftonline.com][email][select]
            logger.debug("Wait for [login.microsoftonline.com][email][select]")
            logger.debug("Select `email` on [login.microsoftonline.com][email][select]")
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//div[@data-test-id="{self.account.Letus.email}"]')
                )
            ).click()
        except:
            # NOTE:wait [login.microsoftonline.com][email][input]
            logger.debug("Wait for [login.microsoftonline.com][email][input]")
            logger.debug("Input `email` on [login.microsoftonline.com][email][input]")
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, "loginfmt"))
            ).send_keys(self.account.Letus.email)
            logger.debug("Click `next` on [login.microsoftonline.com][email][input]")
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.ID, "idSIButton9") and (By.XPATH, '//input[@value="Next"]')
                )
            ).click()

        # NOTE:wait [login.microsoftonline.com][password]
        logger.debug("Wait for [login.microsoftonline.com][password]")
        logger.debug("Input `password` on [login.microsoftonline.com][password]")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "passwd"))
        ).send_keys(self.account.Letus.password)
        logger.debug("Click `sign in` on [login.microsoftonline.com][password]")
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located(
                (By.ID, "idSIButton9") and (By.XPATH, '//input[@value="Sign in"]')
            )
        ).click()

        # NOTE:check [login.microsoftonline.com][password][error]
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "passwordError"))
            )
        except:
            logger.debug("Password is Valid")
        else:
            logger.error("Password Error")
            raise ValueError(logger.c("PasswordError"))

        # NOTE:wait [login.microsoftonline.com][DontShowAgain]
        logger.debug("Wait for [login.microsoftonline.com][DontShowAgain]")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "DontShowAgain"))
        ).click()
        logger.debug("Click `yes` on [login.microsoftonline.com][DontShowAgain]")
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located(
                (By.ID, "idSIButton9") and (By.XPATH, '//input[@value="Yes"]')
            )
        ).click()
        logger.info("Microsoft Login Success")

    def _load_cookie(self):
        cookies = self.driver.get_cookies()
        new_cookies = []
        for new_cookie in cookies:
            if "MoodleSession" in new_cookie["name"]:
                cookie = Cookie(
                    name=new_cookie["name"],
                    value=new_cookie["value"],
                    year=new_cookie["name"].replace("MoodleSession", ""),
                )
                new_cookies.append(cookie)
                text = f'"\33[36mMoodleSession{cookie.year}\33[0m": "\33[36m{cookie.value}\33[0m"'
                logger.info("Cookie found: {" + text + "}")
        if isinstance(self.account.Letus, LetusUserWithCookies):
            for new_cookie in new_cookies:
                for cookie in self.account.Letus.cookies:
                    if new_cookie.year == cookie.year:
                        cookie.value = new_cookie.value
                        break
                else:
                    self.account.Letus.cookies.append(new_cookie)
        else:
            self.account.Letus.cookies = new_cookies
            self.account.Letus = LetusUser.from_api(
                {
                    "student_id": self.account.student_id,
                    "Letus": self.account.Letus.to_api(),
                }
            )

    def register(self):
        self._register()

    def login(self):
        logger.debug("Login to letus")
        if isinstance(self.account.Letus, LetusUserWithCookies):
            for cookie in self.account.Letus.cookies:
                text = f'"\33[36m{cookie.name}\33[0m": "\33[36m{cookie.value}\33[0m"'
                logger.info("Cookie found: {" + text + "}")
        else:
            logger.warn("Cookie not found")
        self._register()


class Authenticator(AuthController):
    def __init__(self, account: AccountBase, socket_client_id: str = ""):
        AuthController.__init__(self, account, socket_client_id)

    ### DO NOT ALLOW WHEN USING SOCKET_IO ###
    async def register(self):
        if self.use_socket_io:
            return
        loop = TaskManager.get_loop()
        await loop.run_in_executor(None, super().register)

    async def login(self):
        if self.use_socket_io:
            return
        loop = TaskManager.get_loop()
        await loop.run_in_executor(None, super().login)

    ### ALLOW ONLY WHEN USING SOCKET_IO ###
    async def login_via_socket(self):
        if not self.use_socket_io:
            return
        loop = TaskManager.get_loop()
        await loop.run_in_executor(None, super().register)
