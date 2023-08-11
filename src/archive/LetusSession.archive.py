import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.Letus.LetusAccount import LetusAccount
from src.util import dotenv_path
from src.util.logger import Logger
from src.util import auth_url, origin_url, year


class LetusSession:
    def __init__(self):
        load_dotenv(verbose=True)
        self.__dotenv_path = dotenv_path
        load_dotenv(self.__dotenv_path)
        self.__logger = Logger(self.__class__.__name__)

        # get environment variables
        CHROME_DRIVER_PATH = os.environ.get('CHROME_DRIVER_PATH')
        if CHROME_DRIVER_PATH is None: raise ValueError('CHROME_DRIVER_PATH is not set')
        else: self.CHROME_DRIVER_PATH = CHROME_DRIVER_PATH

    def register(self, LA: LetusAccount):
        self.__logger.emit('LetusSession:register:Start', '202', 'Register to letus', self.register.__name__)
        self.service = Service(self.CHROME_DRIVER_PATH)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.__login_letus(LA)
        self.load_cookie(LA)

    def login(self, LA: LetusAccount):
        self.__logger.emit('LetusSession:login:Start', '202', 'Login to letus', self.login.__name__)
        for key in LA.cookie.keys():
            if key == f'MoodleSession{LA.year}':
                cookie = LA.cookie[key]
                self.__logger.emit('LetusSession:login:Cookie:Found', '202', 'Cookie found', self.login.__name__)
                self.__logger.info(f'{key}: {cookie}', self.login.__name__)
                break
        else:
            self.__logger.emit('LetusSession:login:Cookie:NotFound', '404', 'Cookie not found', self.login.__name__)
        self.register(LA)

    def __login_letus(self, LA: LetusAccount):
        self.__logger.emit('LetusSession:login:__login_letus:Start', '202', 'Login to letus', self.__login_letus.__name__)
        self.driver.get(auth_url)
        WebDriverWait(self.driver, 3).until(EC.url_contains('https://idp.admin.tus.ac.jp/idp/profile/SAML2/Redirect/SSO'))
        self.driver.find_element(By.NAME, '_eventId_ChooseSam2').click()
        timeout = time.time() + 60
        while True:
            if origin_url in self.driver.current_url:
                self.__logger.emit('LetusSession:login:__login_letus:Success', '200', 'Letus Login Success', self.__login_letus.__name__)
                break
            elif 'https://login.microsoftonline.com' in self.driver.current_url:
                while True:
                    try:
                        self.__login_microsoft(LA)
                    except ValueError as e:
                        if 'LetusSession:login:__login_microsoft:PasswordError' in str(e):
                            raise ValueError('LetusSession:login:__login_letus:PasswordError')
                    except:
                        self.__logger.error('Retrying...')
                        continue
                    else:
                        break
            elif time.time() > timeout:
                self.__logger.emit('LetusSession:login:__login_letus:Timeout', '504', 'Timeout while accessing Letus Login Page', self.__login_letus.__name__)
                raise TimeoutError('LetusSession:login:__login_letus:Timeout')
            else:
                continue

    def __login_microsoft(self, LA: LetusAccount):
        self.__logger.emit('LetusSession:login:__login_microsoft:Start', '202', 'Login to Microsoft', self.__login_microsoft.__name__)
        self.driver.get(auth_url)

        # wait [idp.admin.tus.ac.jp]
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.NAME, '_eventId_ChooseSam2'))).click()

        # wait [login.microsoftonline.com][email]
        self.__logger.emit('LetusSession:login:__login_microsoft:Email', '202', 'Email field', self.__login_microsoft.__name__)
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        try:
            # wait [login.microsoftonline.com][email][select]
            self.__logger.emit('LetusSession:login:__login_microsoft:Email:Select', '202', 'Email select', self.__login_microsoft.__name__)
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, f'//div[@data-test-id="{LA.email}"]'))).click()
        except:
            # wait [login.microsoftonline.com][email][input]
            self.__logger.emit('LetusSession:login:__login_microsoft:Email:Input', '202', 'Email input', self.__login_microsoft.__name__)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.NAME, 'loginfmt'))).send_keys(LA.email)
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'idSIButton9') and (By.XPATH, '//input[@value="Next"]'))).click()

        # wait [login.microsoftonline.com][password]
        self.__logger.emit('LetusSession:login:__login_microsoft:Password', '202', 'Password field', self.__login_microsoft.__name__)
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.NAME, 'passwd'))).send_keys(LA.encrypted_password)
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'idSIButton9') and (By.XPATH, '//input[@value="Sign in"]'))).click()

        # check [login.microsoftonline.com][password][error]
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'passwordError')))
        except:
            self.__logger.emit('LetusSession:login:__login_microsoft:PasswordValid', '202', 'Password Valid', self.__login_microsoft.__name__)
        else:
            self.__logger.emit('LetusSession:login:__login_microsoft:PasswordError', '401', 'Password Error', self.__login_microsoft.__name__)
            raise ValueError('LetusSession:login:__login_microsoft:PasswordError')

        # # wait [login.microsoftonline.com][MFA]
        # WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        # try:
        #     # wait [login.microsoftonline.com][MFA][select]
        #     self.__logger.emit('LetusSession:login:__login_microsoft:MFA:Select', '202', 'Selecting default MFA method', self.__login_microsoft.__name__)
        #     WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '//div[@aria-describedby="idDiv_SAOTCS_Title"]'))).click()
        # except:
        #     pass

        # # check [login.microsoftonline.com][MFA][option]
        # try:
        #     # wait element
        #     self.__logger.emit('LetusSession:login:__login_microsoft:MFA:Select:CheckMethod', '202', 'Checking MFA method', self.__login_microsoft.__name__)
        #     WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.NAME, 'mfaAuthMethod')))
        #     mfa_auth_method = self.driver.find_element(By.NAME, 'mfaAuthMethod').get_attribute('value')
        #     if not mfa_auth_method:
        #         raise ValueError('LetusSession:login:__login_microsoft:MFA:OptionError')
        # except:
        #     self.__logger.emit('LetusSession:login:__login_microsoft:MFA:OptionError', '401', 'MFA Option Not Found', self.__login_microsoft.__name__)
        #     raise ValueError('LetusSession:login:__login_microsoft:MFA:OptionError')
        # else:
        #     self.__logger.emit('LetusSession:login:__login_microsoft:MFA:OptionValid', '202', 'MFA Option Valid', self.__login_microsoft.__name__)
        #     # PhoneAppNotification,TwoWayVoiceMobile,PhoneAppOTP,OneWaySMS
        #     if mfa_auth_method == 'PhoneAppNotification':
        #         try:
        #             self.__login_microsoft_PhoneAppNotification()
        #         except Exception as e:
        #             self.__logger.emit('LetusSession:login:__login_microsoft:MFA:PhoneAppNotification:Error', '401', 'MFA PhoneAppNotification Error', self.__login_microsoft.__name__)
        #             raise Exception('LetusSession:login:__login_microsoft:MFA:PhoneAppNotification:Error')
        #         else:
        #             self.__logger.emit('LetusSession:login:__login_microsoft:MFA:PhoneAppNotification:Success', '202', 'MFA PhoneAppNotification Success', self.__login_microsoft.__name__)
        #     elif mfa_auth_method == 'OneWaySMS':
        #         try:
        #             self.__login_microsoft_OneWaySMS()
        #         except Exception as e:
        #             self.__logger.emit('LetusSession:login:__login_microsoft:MFA:OneWaySMS:Error', '401', 'MFA OneWaySMS Error', self.__login_microsoft.__name__)
        #             raise Exception('LetusSession:login:__login_microsoft:MFA:OneWaySMS:Error')
        #         else:
        #             self.__logger.emit('LetusSession:login:__login_microsoft:MFA:OneWaySMS:Success', '202', 'MFA OneWaySMS Success', self.__login_microsoft.__name__)
        #     elif mfa_auth_method == 'PhoneAppOTP':
        #         try:
        #             self.__login_microsoft_PhoneAppOTP()
        #         except Exception as e:
        #             self.__logger.emit('LetusSession:login:__login_microsoft:MFA:PhoneAppOTP:Error', '401', 'MFA PhoneAppOTP Error', self.__login_microsoft.__name__)
        #             raise Exception('LetusSession:login:__login_microsoft:MFA:PhoneAppOTP:Error')
        #         else:
        #             self.__logger.emit('LetusSession:login:__login_microsoft:MFA:PhoneAppOTP:Success', '202', 'MFA PhoneAppOTP Success', self.__login_microsoft.__name__)

        # wait [login.microsoftonline.com][MFA][DontShowAgain]
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.NAME, 'DontShowAgain'))).click()
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'idSIButton9') and (By.XPATH, '//input[@value="Yes"]'))).click()
        self.__logger.emit('LetusSession:login:__login_microsoft:MFA:Success', '200', 'MFA Success', self.__login_microsoft.__name__)
        self.__logger.emit('LetusSession:login:__login_microsoft:Success', '200', 'Microsoft Login Success', self.__login_microsoft.__name__)

    # def __login_microsoft_PhoneAppNotification(self):
    #     self.__logger.emit('LetusSession:login:__login_microsoft:MFA:PhoneAppNotification:Start', '202', 'MFA PhoneAppNotification', self.__login_microsoft.__name__)
    #     WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    #     self.__logger.emit('LetusSession:login:__login_microsoft:MFA:PhoneAppNotification:Waiting', '202', 'Waiting for MFA...', self.__login_microsoft.__name__)
    #     WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.NAME, 'rememberMFA'))).click()

    # def __login_microsoft_OneWaySMS(self):
    #     self.__logger.emit('LetusSession:login:__login_microsoft:MFA:OneWaySMS:Start', '202', 'MFA OneWaySMS', self.__login_microsoft.__name__)
    #     # WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    #     self.__logger.emit('LetusSession:login:__login_microsoft:MFA:OneWaySMS:Waiting', '202', 'Waiting for MFA...', self.__login_microsoft.__name__)
    #     # WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.NAME, 'rememberMFA'))).click()

    # def __login_microsoft_PhoneAppOTP(self):
    #     self.__logger.emit('LetusSession:login:__login_microsoft:MFA:PhoneAppOTP:Start', '202', 'MFA PhoneAppOTP', self.__login_microsoft.__name__)
    #     # WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    #     self.__logger.emit('LetusSession:login:__login_microsoft:MFA:PhoneAppOTP:Waiting', '202', 'Waiting for MFA...', self.__login_microsoft.__name__)
    #     # WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.NAME, 'rememberMFA'))).click()

    def load_cookie(self, LA: LetusAccount):
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == f'MoodleSession{LA.year}':
                self.__new_cookie = cookie['value']
                self.__logger.info(f'MoodleSession{LA.year} Cookie: {self.__new_cookie}', self.load_cookie.__name__)
                print(f'MoodleSession{LA.year} Cookie: {self.__new_cookie}', self.load_cookie.__name__)
                break

        if (self.__new_cookie and isinstance(self.__new_cookie, str)):
            LA.cookie[f'MoodleSession{LA.year}'] = self.__new_cookie
            self.__logger.emit('LetusSession:find_cookie:Success', '200', 'Cookie Found', self.load_cookie.__name__)
