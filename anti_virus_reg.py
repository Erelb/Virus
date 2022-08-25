"""
anti virus for registry
"""
from winreg import *
import win32api
import winreg
import win32event
import threading
from elevate import elevate
import ctypes
import win32con


# constants
VALUES_SYSTEM = ['DisableChangePassword',
                 'DisableLockWorkstation',
                 'NoLogoff']
VALUES_LOCAL_MACHINE = ['DisableTaskMgr',
                        "HideFastUserSwitching"]
REG_PATH_SYSTEM = r"SOFTWARE\\" \
                  r"Microsoft\\Windows\\" \
                  r"CurrentVersion\\Policies\\System"
REG_PATH_EXPLORER = r"SOFTWARE\\" \
                    r"Microsoft\\Windows\\" \
                    r"CurrentVersion\\Policies\\Explorer"


class WatchRegistry(object):
    """
    Handles the changes in the registry
    """

    @staticmethod
    def get_reg(root, path, name):
        """
        prints the value of given registry entry root\\path\value
        creates it if does not exist
        """
        try:
            registry_key = OpenKey(root, path, 0, KEY_READ)
            value, regtype = QueryValueEx(registry_key, name)
            CloseKey(registry_key)
            return value
        except WindowsError as e:
            print("get_reg: ", e)

    @staticmethod
    def set_reg(root, path, name, value):
        """
        sets given  value in the requested
        registry entry root\\path\value
        """
        try:
            CreateKey(root, path)
            registry_key = OpenKey(root, path, 0, KEY_WRITE)
            SetValueEx(registry_key, name, 0, REG_SZ, value)
            CloseKey(registry_key)
        except WindowsError:
            print("Error")

    @staticmethod
    def set_reg2(root, path, name, value):
        """
        sets given  value in the requested
        registry entry root\\path\value
        """
        CreateKey(root, path)
        registry_key = OpenKey(root, path, 0, KEY_WRITE)
        SetValueEx(registry_key, name, 0, REG_DWORD, value)
        CloseKey(registry_key)

    @staticmethod
    def serchForNewValue(root, path):
        """
        goes over the watched folders and checks
        if there is a change
        """
        i = 0
        if root == HKEY_LOCAL_MACHINE:
            names = VALUES_LOCAL_MACHINE
        else:
            names = VALUES_SYSTEM
        while i < len(names):
            try:
                value = WatchRegistry.get_reg(root, path, names[i])
                if value == str(1) or value == 1:
                    MessageBox = ctypes.windll.user32.MessageBoxW
                    yes_no = MessageBox(None,
                                        'A new value named: ' +
                                        str(names[i]) +
                                        ' was added,'
                                        ' do yo want to remove it? ',
                                        'Message',
                                        win32con.MB_YESNO)
                    if yes_no:
                        print(names[i])
                        if names[i] == 'DisableTaskMgr':
                            print(root)
                            print(path)
                            print(names[i])
                            WatchRegistry.set_reg2(root, path, names[i], 0)
                        else:
                            WatchRegistry.set_reg(root, path, names[i], '0')
                i += 1
            except WindowsError:
                i += 1

    @staticmethod
    def notice_changes(root, path):
        """
        notice if there is a change in the
        watched folders
        """
        try:
            key = winreg.OpenKey(
                root,
                path, 0, winreg.KEY_ALL_ACCESS)
            done = False
            while not done:
                evnt = win32event.CreateEvent(None, 0, 0, None)
                win32api.RegNotifyChangeKeyValue(
                    key, 1,
                    win32api.REG_NOTIFY_CHANGE_LAST_SET,
                    evnt, True)
                ret_code = win32event.WaitForSingleObject(evnt, 3000)
                if ret_code == win32con.WAIT_OBJECT_0:
                    print("chANGE")
                    WatchRegistry.serchForNewValue(root, path)
                else:
                    print("ttt")
        except Exception as msg:
            print(msg)


def main():
    """
    Notice if there is a detrimental value that was added
    to the watched folders and enables to remove it
    """
    elevate(show_console=False)
    system_localMachine_thread = threading.Thread(
        target=WatchRegistry.notice_changes,
        args=(HKEY_LOCAL_MACHINE, REG_PATH_SYSTEM))
    system_localMachine_thread.start()
    system_currentUser_thread = threading.Thread(
        target=WatchRegistry.notice_changes,
        args=(HKEY_CURRENT_USER, REG_PATH_SYSTEM))
    system_currentUser_thread.start()
    explorer_currentUser_thread = threading.Thread(
        target=WatchRegistry.notice_changes,
        args=(HKEY_CURRENT_USER, REG_PATH_EXPLORER))
    explorer_currentUser_thread.start()


if __name__ == '__main__':
    main()