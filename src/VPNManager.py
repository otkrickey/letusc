from os import path
import shutil
import threading
from dotenv import load_dotenv
import subprocess
from src.util.logger import Log

from src.util.static import env


class VPNManager:
    _is_backed_up = False
    _is_installed = False
    _is_connected = False
    _is_alive = False

    def __init__(self, show_cli_log=False):
        # load environment variables
        home = env("HOME")
        host = env("VPN_HOST")
        user = env("VPN_USER")
        passwd = env("VPN_PASS")
        cli_source = env("VPN_CLI_SOURCE")
        cli_path = env("VPN_CLI_PATH")
        cli_version = env("VPN_CLI_VERSION")

        # set environment variables
        self.home = home
        self.host, self.user, self.passwd = host, user, passwd
        self.cli_source = cli_source
        self.cli_path = cli_path
        self.cli_version = cli_version

        # set config
        self.show_cli_log = show_cli_log

    @staticmethod
    def backup_dns():
        __logger = Log("VPNManager.backup_dns")
        __logger_cp = Log("cp.backup_dns", True)
        __logger.info("Backing up DNS settings")
        src = "/etc/resolv.conf"
        dst = "/mnt/c/Users/rtkfi/dev/settings/resolv.conf"
        command_cp = ["sudo", "cp", src, dst]
        if not VPNManager._is_backed_up:
            process_cp = subprocess.Popen(
                command_cp,
                stdout=subprocess.PIPE,
            )
            while True:
                if not process_cp.stdout:
                    break
                line = process_cp.stdout.readline()
                if not line:
                    break
                line_str = line.decode("utf-8").strip()
                __logger_cp.debug(line_str)
            __logger.info("DNS backup file created")
        else:
            __logger.warn("DNS backup file already exists")

    @staticmethod
    def fix_dns():
        __logger = Log("VPNManager.fix_dns")
        __logger_cp = Log("cp.fix_dns", True)
        __logger.info("Fixing DNS settings")
        src = "/mnt/c/Users/rtkfi/dev/settings/resolv.conf"
        dst = "/mnt/wsl/resolv.conf"
        command_cp = ["suso", "cp", src, dst]
        if path.exists(src):
            process_cp = subprocess.Popen(
                command_cp,
                stdout=subprocess.PIPE,
            )
            while True:
                if not process_cp.stdout:
                    break
                line = process_cp.stdout.readline()
                if not line:
                    break
                line_str = line.decode("utf-8").strip()
                __logger_cp.debug(line_str)
            __logger.info("DNS settings fixed")
        else:
            __logger.warn("DNS backup file does not exist")
            __logger.warn("Cannot fix DNS settings, need to reboot")

    def unzip(self):
        __logger = Log("VPNManager.unzip")
        __logger_Tar = Log("Tar.unzip", self.show_cli_log)
        __logger.info("Unzipping Cisco VPN client")
        command_unzip = [
            "tar",
            "zxf",
            self.cli_source,
            "-C",
            f"{self.home}/setting/cisco/",
        ]
        process_unzip = subprocess.Popen(
            command_unzip,
            stdout=subprocess.PIPE,
        )
        while True:
            if not process_unzip.stdout:
                break
            line = process_unzip.stdout.readline()
            if not line:
                break
            line_str = line.decode("utf-8").strip()
            __logger_Tar.debug(line_str)
        process_unzip.wait()

    def install(self):
        __logger = Log("VPNManager.install")
        __logger_VPN = Log("CiscoVPN.install", self.show_cli_log)
        self.unzip()
        __logger.info("Installing Cisco VPN client")
        # install the source
        cwd = f"{self.home}/setting/cisco/{self.cli_version}/vpn"
        command_install = ["yes | sudo ./vpn_install.sh"]
        process_install = subprocess.Popen(
            command_install,
            stdout=subprocess.PIPE,
            cwd=cwd,
            shell=True,
        )
        while True:
            if not process_install.stdout:
                break
            line = process_install.stdout.readline()
            if not line:
                break
            line_str = line.decode("utf-8").strip()
            __logger_VPN.debug(line_str)
        process_install.wait()

    @staticmethod
    def uninstall():
        __logger = Log("VPNManager.uninstall")
        __logger.info("Uninstalling Cisco VPN client")
        cli_path = "/opt/cisco/"
        if path.exists(cli_path):
            shutil.rmtree(cli_path)
            __logger.info("Cisco VPN client uninstalled")
        else:
            __logger.warn("Cisco VPN client not found")

    def connect(self):
        __logger = Log("VPNManager.connect")
        __logger_VPN = Log("CiscoVPN.connect", self.show_cli_log)
        __logger.info("Connecting to VPN")
        connected = False
        failed = False
        errorMessages = []
        command_connect = [
            self.cli_path,
            "-s",
            "connect",
            self.host,
        ]
        __logger.info(f"VPN: {' '.join(command_connect)}")
        process_connect = subprocess.Popen(
            command_connect,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        while True:
            if not process_connect.stdout:
                break
            if not process_connect.stdin:
                break
            line = process_connect.stdout.readline()
            if not line:
                break
            line_str = line.decode("utf-8").strip()
            __logger_VPN.debug(line_str)

            if ">> Please enter your username and password." in line_str:
                process_connect.stdin.write(f"{self.user}\n".encode("utf-8"))
                process_connect.stdin.flush()
                process_connect.stdin.write(f"{self.passwd}\n".encode("utf-8"))
                process_connect.stdin.flush()
            if "Connected" in line_str:
                connected = True
            if "error: " in line_str:
                failed = True
                errorMessages.append(line_str)
        process_connect.wait()
        if connected:
            __logger.info("Connected to VPN")
        elif failed:
            __logger.error("Failed to connect to VPN")
            for errorMessage in errorMessages:
                __logger.error(errorMessage)
        else:
            __logger.warn("Failed to connect to VPN")

    def disconnect(self):
        __logger = Log("VPNManager.disconnect")
        __logger_VPN = Log("CiscoVPN.disconnect", self.show_cli_log)
        __logger.info("Disconnecting from VPN")
        command_disconnect = [
            self.cli_path,
            "-s",
            "disconnect",
        ]
        process_disconnect = subprocess.Popen(
            command_disconnect,
            stdout=subprocess.PIPE,
        )
        while True:
            if not process_disconnect.stdout:
                break
            line = process_disconnect.stdout.readline()
            if not line:
                break
            line_str = line.decode("utf-8").strip()
            __logger_VPN.debug(line_str)
        process_disconnect.wait()
        __logger.info("Disconnected from VPN")

    def status(self):
        __logger = Log("VPNManager.status")
        __logger_VPN = Log("CiscoVPN.status", self.show_cli_log)
        __logger.info("Checking VPN status")
        is_connected = False
        is_alive = False
        command_status = [
            self.cli_path,
            "-s",
            "status",
        ]
        process_status = subprocess.Popen(
            command_status,
            stdout=subprocess.PIPE,
        )
        while True:
            if not process_status.stdout:
                break
            line = process_status.stdout.readline()
            if not line:
                break
            line_str = line.decode("utf-8").strip()
            __logger_VPN.debug(line_str)
            if ">> state: Connected" in line_str:
                is_connected = True
                is_alive = True
            elif ">> state: Disconnected" in line_str:
                is_connected = False
                is_alive = True
        process_status.wait()
        VPNManager._is_connected = is_connected
        __logger.info(f"VPN connected: \33[32m{self._is_connected}\33[0m")
        VPNManager._is_alive = is_alive
        __logger.info(f"VPN alive: \33[32m{self._is_alive}\33[0m")


class VPNController:
    _Manager = None
    cv = threading.Condition()
    thread = None

    def __init__(self, show_cli_log=False):
        if VPNController._Manager is None:
            VPNController._Manager = VPNManager(show_cli_log)
            if VPNController.thread is None:
                VPNController.thread = threading.Thread(target=self._status_worker)
                VPNController.thread.daemon = True
                VPNController.thread.start()

        VPNController._Manager.backup_dns()
        VPNController._Manager.install()
        VPNController._Manager.connect()

    def _status_worker(self):
        __logger = Log("VPNController.status_worker")
        __logger.info("Starting VPN status worker")
        interval = int(env("VPN_STATUS_INTERVAL")) * 60  # minutes to seconds
        # first check
        self.status()
        while True:
            with VPNController.cv:
                __logger.info("Waiting for VPN status worker")
                VPNController.cv.wait(interval)
                __logger.info(f"[every {interval} seconds] Checking VPN status")
                assert VPNController._Manager is not None
                VPNController._Manager.status()

    @staticmethod
    def status():
        __logger = Log("VPNController.status")
        __logger.info("Checking VPN status (blocking)")
        with VPNController.cv:
            assert VPNController._Manager is not None
            VPNController._Manager.status()
            VPNController.cv.notify()

    @staticmethod
    def connect():
        __logger = Log("VPNController.connect")
        __logger.info("Connecting to VPN")
        with VPNController.cv:
            assert VPNController._Manager is not None
            VPNController._Manager.status()
            if not VPNController._Manager._is_installed:
                VPNController._Manager.install()
            if not VPNController._Manager._is_alive:
                VPNController._Manager.fix_dns()
                VPNController._Manager.install()
            if not VPNController._Manager._is_connected:
                VPNController._Manager.connect()
            VPNController.cv.notify()


# TODO: VPNManager
# - create auto method
#    - automatically connect to VPN
#    - run auto() per hour default
#    - when receive request to connect to VPN & 10 minutes have passed since last auto()
#    - order
#        1. check() to see if CLI is usable
#            - if not, uninstall() -> install()
#        2. status() to see if connected to VPN
#            - if connected & an hour has passed since last auto(), disconnect()
#        3. connect() to connect to VPN
