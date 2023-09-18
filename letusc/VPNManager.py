import subprocess
import threading
from os import path

from letusc.logger import L
from letusc.util import env

__all__ = [
    "VPNManager",
]


class VPNController:
    _l = L()
    _is_backed_up = False
    _is_installed = False
    _is_connected = False
    _is_alive = False

    def __init__(self, show_cli_log=False):
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__init__")
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
        _l = L(VPNController.__name__).gm("backup_dns")
        _l_cp = L(VPNController.__name__).gm("cp.backup_dns")
        _l.info("Backing up DNS settings")
        src = "/etc/resolv.conf"
        dst = "/mnt/c/Users/rtkfi/dev/settings/resolv.conf"
        command_cp = ["sudo", "cp", src, dst]
        if not VPNController._is_backed_up:
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
                _l_cp.debug(line_str)
            _l.info("DNS backup file created")
        else:
            _l.warn("DNS backup file already exists")

    @staticmethod
    def fix_dns():
        _l = L(VPNController.__name__).gm("fix_dns")
        _l_cp = L(VPNController.__name__).gm("cp.fix_dns")
        _l.info("Fixing DNS settings")
        src = "/mnt/c/Users/rtkfi/dev/settings/resolv.conf"
        dst = "/mnt/wsl/resolv.conf"
        command_cp = ["sudo", "cp", src, dst]
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
                _l_cp.debug(line_str)
            _l.info("DNS settings fixed")
        else:
            _l.warn("DNS backup file does not exist")
            _l.warn("Cannot fix DNS settings, need to reboot")

    def unzip(self):
        _l = L(VPNController.__name__).gm("unzip")
        _l_Tar = L(VPNController.__name__).gm("tar.unzip")
        _l.info("Unzipping Cisco VPN client")
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
            _l_Tar.debug(line_str)
        process_unzip.wait()

    def install(self):
        _l = L(VPNController.__name__).gm("install")
        _l_VPN = L(VPNController.__name__).gm("CiscoVPN.install")
        self.unzip()
        _l.info("Installing Cisco VPN client")
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
            _l_VPN.debug(line_str)
        process_install.wait()
        self.status()

    @staticmethod
    def uninstall():
        _l = L(VPNController.__name__).gm("uninstall")
        _l_rm = L(VPNController.__name__).gm("rm.uninstall")
        _l.info("Uninstalling Cisco VPN client")
        cli_path = "/opt/cisco/"
        command_rm = ["sudo", "rm", "-rf", cli_path]
        if path.exists(cli_path):
            process_rm = subprocess.Popen(
                command_rm,
                stdout=subprocess.PIPE,
            )
            while True:
                if not process_rm.stdout:
                    break
                line = process_rm.stdout.readline()
                if not line:
                    break
                line_str = line.decode("utf-8").strip()
                _l_rm.debug(line_str)
            _l.info("Cisco VPN client uninstalled")
        else:
            _l.warn("Cisco VPN client not found")

    def connect(self):
        _l = L(VPNController.__name__).gm("connect")
        _l_VPN = L(VPNController.__name__).gm("CiscoVPN.connect")
        _l.info("Connecting to VPN")
        connected = False
        failed = False
        errorMessages = []
        command_connect = [
            self.cli_path,
            "-s",
            "connect",
            self.host,
        ]
        _l.info(f"VPN: {' '.join(command_connect)}")
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
            _l_VPN.debug(line_str)

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
            _l.info("Connected to VPN")
        elif failed:
            _l.error("Failed to connect to VPN")
            for errorMessage in errorMessages:
                _l.error(errorMessage)
            self.status()
            self.connect()
        else:
            _l.warn("Failed to connect to VPN")

    def disconnect(self):
        _l = L(VPNController.__name__).gm("disconnect")
        _l_VPN = L(VPNController.__name__).gm("CiscoVPN.disconnect")
        _l.info("Disconnecting from VPN")
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
            _l_VPN.debug(line_str)
        process_disconnect.wait()
        _l.info("Disconnected from VPN")

    def status(self):
        _l = L(VPNController.__name__).gm("status")
        _l_VPN = L(VPNController.__name__).gm("CiscoVPN.status")
        _l.info("Checking VPN status")
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
            _l_VPN.debug(line_str)
            if ">> state: Connected" in line_str:
                is_connected = True
                is_alive = True
            elif ">> state: Disconnected" in line_str:
                is_connected = False
                is_alive = True
        process_status.wait()
        VPNController._is_connected = is_connected
        _l.info(f"VPN connected: \33[32m{self._is_connected}\33[0m")
        VPNController._is_alive = is_alive
        _l.info(f"VPN alive: \33[32m{self._is_alive}\33[0m")


class VPNManager:
    _l = L()
    _Manager = None
    cv = threading.Condition()
    thread = None

    def __init__(self, show_cli_log=False):
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__init__")
        if VPNManager._Manager is None:
            VPNManager._Manager = VPNController(show_cli_log)
            if VPNManager.thread is None:
                VPNManager.thread = threading.Thread(target=self._status_worker)
                VPNManager.thread.daemon = True
                VPNManager.thread.start()

        VPNManager._Manager.backup_dns()
        VPNManager._Manager.install()
        VPNManager._Manager.connect()

    def _status_worker(self):
        _l = L(VPNManager.__name__).gm("status_worker")
        _l.info("Starting VPN status worker")
        interval = int(env("VPN_STATUS_INTERVAL")) * 60  # minutes to seconds
        self.status()
        while True:
            with VPNManager.cv:
                _l.info("Waiting for VPN status worker")
                VPNManager.cv.wait(interval)
                _l.info(f"[every {interval} seconds] Checking VPN status")
                assert VPNManager._Manager is not None
                VPNManager._Manager.status()

    @staticmethod
    def status():
        _l = L(VPNManager.__name__).gm("status")
        _l.info("Checking VPN status (blocking)")
        with VPNManager.cv:
            assert VPNManager._Manager is not None
            VPNManager._Manager.status()
            VPNManager.cv.notify()

    @staticmethod
    def connect():
        _l = L(VPNManager.__name__).gm("connect")
        _l.info("Connecting to VPN")
        with VPNManager.cv:
            assert VPNManager._Manager is not None
            VPNManager._Manager.status()
            if not VPNManager._Manager._is_installed:
                VPNManager._Manager.install()
            if not VPNManager._Manager._is_alive:
                VPNManager._Manager.uninstall()
                VPNManager._Manager.fix_dns()
                VPNManager._Manager.install()
            if not VPNManager._Manager._is_connected:
                VPNManager._Manager.connect()
            VPNManager.cv.notify()
