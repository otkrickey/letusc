import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .logger import get_logger
from .models.account import AccountBase
from .models.cookie import Cookie
from .models.event import Progress, Status
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
            progress = Progress(
                self.sid,
                "AuthController:_register",
                "Register to letus",
                Status.START,
                2,
            )
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
            progress = Progress(
                self.sid,
                "AuthController:_login_letus",
                "Login to letus",
                Status.START,
                3,
            )
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
                if self.use_socket_io:
                    progress = Progress(
                        self.sid,
                        "AuthController:_login_letus",
                        "Letus Login Success",
                        Status.SUCCESS,
                        20,
                    )
                    self.loop.create_task(self.sio_client.send_progress(progress))
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
                        if self.use_socket_io:
                            progress = Progress(
                                self.sid,
                                "AuthController:_login_letus",
                                "Retrying...",
                                Status.WAIT,
                                17,
                            )
                            self.loop.create_task(
                                self.sio_client.send_progress(progress)
                            )
                        continue
                    else:
                        break
            else:
                continue

    def _login_ms(self):
        logger.debug("Login to Microsoft")
        if self.use_socket_io:
            progress = Progress(
                self.sid,
                "AuthController:_login_ms",
                "Login to Microsoft",
                Status.START,
                4,
            )
            self.loop.create_task(self.sio_client.send_progress(progress))

        auth_url = URLManager.getAuth()
        self.driver.get(auth_url)

        # NOTE:wait [idp.admin.tus.ac.jp]
        logger.debug("Wait for [idp.admin.tus.ac.jp]")
        if self.use_socket_io:
            progress = Progress(
                self.sid,
                "AuthController:_login_ms",
                "Wait for [idp.admin.tus.ac.jp]",
                Status.WAIT,
                5,
            )
            self.loop.create_task(self.sio_client.send_progress(progress))

        logger.debug("Click `next` on [idp.admin.tus.ac.jp]")
        if self.use_socket_io:
            progress = Progress(
                self.sid,
                "AuthController:_login_ms",
                "Click `next` on [idp.admin.tus.ac.jp]",
                Status.CLICK,
                6,
            )
            self.loop.create_task(self.sio_client.send_progress(progress))
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.NAME, "_eventId_ChooseSam2"))
        ).click()

        # NOTE:wait [login.microsoftonline.com][email]
        logger.debug("Wait for [login.microsoftonline.com][email]")
        if self.use_socket_io:
            progress = Progress(
                self.sid,
                "AuthController:_login_ms",
                "Wait for [login.microsoftonline.com][email]",
                Status.WAIT,
                7,
            )
            self.loop.create_task(self.sio_client.send_progress(progress))
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        try:
            # NOTE:wait [login.microsoftonline.com][email][select]
            logger.debug("Wait for [login.microsoftonline.com][email][select]")
            if self.use_socket_io:
                progress = Progress(
                    self.sid,
                    "AuthController:_login_ms",
                    "Wait for [login.microsoftonline.com][email][select]",
                    Status.WAIT,
                    8,
                )
                self.loop.create_task(self.sio_client.send_progress(progress))

            logger.debug("Select `email` on [login.microsoftonline.com][email][select]")
            if self.use_socket_io:
                progress = Progress(
                    self.sid,
                    "AuthController:_login_ms",
                    "Select `email` on [login.microsoftonline.com][email][select]",
                    Status.CLICK,
                    9,
                )
                self.loop.create_task(self.sio_client.send_progress(progress))
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//div[@data-test-id="{self.account.Letus.email}"]')
                )
            ).click()
        except:
            # NOTE:wait [login.microsoftonline.com][email][input]
            logger.debug("Wait for [login.microsoftonline.com][email][input]")
            if self.use_socket_io:
                progress = Progress(
                    self.sid,
                    "AuthController:_login_ms",
                    "Wait for [login.microsoftonline.com][email][input]",
                    Status.WAIT,
                    10,
                )
                self.loop.create_task(self.sio_client.send_progress(progress))
            logger.debug("Input `email` on [login.microsoftonline.com][email][input]")
            if self.use_socket_io:
                progress = Progress(
                    self.sid,
                    "AuthController:_login_ms",
                    "Input `email` on [login.microsoftonline.com][email][input]",
                    Status.INPUT,
                    11,
                )
                self.loop.create_task(self.sio_client.send_progress(progress))
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, "loginfmt"))
            ).send_keys(self.account.Letus.email)
            logger.debug("Click `next` on [login.microsoftonline.com][email][input]")
            if self.use_socket_io:
                progress = Progress(
                    self.sid,
                    "AuthController:_login_ms",
                    "Click `next` on [login.microsoftonline.com][email][input]",
                    Status.CLICK,
                    12,
                )
                self.loop.create_task(self.sio_client.send_progress(progress))
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.ID, "idSIButton9") and (By.XPATH, '//input[@value="Next"]')
                )
            ).click()

        # NOTE:wait [login.microsoftonline.com][password]
        logger.debug("Wait for [login.microsoftonline.com][password]")
        if self.use_socket_io:
            progress = Progress(
                self.sid,
                "AuthController:_login_ms",
                "Wait for [login.microsoftonline.com][password]",
                Status.WAIT,
                13,
            )
            self.loop.create_task(self.sio_client.send_progress(progress))
        logger.debug("Input `password` on [login.microsoftonline.com][password]")
        if self.use_socket_io:
            progress = Progress(
                self.sid,
                "AuthController:_login_ms",
                "Input `password` on [login.microsoftonline.com][password]",
                Status.INPUT,
                14,
            )
            self.loop.create_task(self.sio_client.send_progress(progress))
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "passwd"))
        ).send_keys(self.account.Letus.password)
        logger.debug("Click `sign in` on [login.microsoftonline.com][password]")
        if self.use_socket_io:
            progress = Progress(
                self.sid,
                "AuthController:_login_ms",
                "Click `sign in` on [login.microsoftonline.com][password]",
                Status.CLICK,
                15,
            )
            self.loop.create_task(self.sio_client.send_progress(progress))
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
            if self.use_socket_io:
                progress = Progress(
                    self.sid,
                    "AuthController:_login_ms",
                    "Password is Valid",
                    Status.SUCCESS,
                    16,
                )
                self.loop.create_task(self.sio_client.send_progress(progress))
        else:
            logger.error("Password Error")
            if self.use_socket_io:
                progress = Progress(
                    self.sid,
                    "AuthController:_login_ms",
                    "Password Error",
                    Status.ERROR,
                    16,
                )
                self.loop.create_task(self.sio_client.send_progress(progress))
            raise ValueError(logger.c("PasswordError"))

        # NOTE:wait [login.microsoftonline.com][DontShowAgain]
        logger.debug("Wait for [login.microsoftonline.com][DontShowAgain]")
        if self.use_socket_io:
            progress = Progress(
                self.sid,
                "AuthController:_login_ms",
                "Wait for [login.microsoftonline.com][DontShowAgain]",
                Status.WAIT,
                17,
            )
            self.loop.create_task(self.sio_client.send_progress(progress))
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "DontShowAgain"))
        ).click()
        logger.debug("Click `yes` on [login.microsoftonline.com][DontShowAgain]")
        if self.use_socket_io:
            progress = Progress(
                self.sid,
                "AuthController:_login_ms",
                "Click `yes` on [login.microsoftonline.com][DontShowAgain]",
                Status.CLICK,
                18,
            )
            self.loop.create_task(self.sio_client.send_progress(progress))
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located(
                (By.ID, "idSIButton9") and (By.XPATH, '//input[@value="Yes"]')
            )
        ).click()
        logger.info("Microsoft Login Success")
        if self.use_socket_io:
            progress = Progress(
                self.sid,
                "AuthController:_login_ms",
                "Microsoft Login Success",
                Status.SUCCESS,
                19,
            )
            self.loop.create_task(self.sio_client.send_progress(progress))

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
                if self.use_socket_io:
                    progress = Progress(
                        self.sid,
                        "AuthController:_load_cookie",
                        "Cookie found",
                        Status.SUCCESS,
                        21,
                    )
                    self.loop.create_task(self.sio_client.send_progress(progress))
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
