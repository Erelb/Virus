"""
The Gui interface of the server
"""

import wx
from Server2 import *

# constants
STILL_ALIVE = '1'
RELEASE_REQUEST = "release"
PORT = 1729
IP = "0.0.0.0"


class ListInterface(wx.Frame):
    """
    The List interface
    """
    def __init__(self, *args, **kw):
        """
        constructor
        """
        super(ListInterface, self).__init__(*args, **kw)
        self.timer = wx.Timer(self)
        self.server = None
        self.ipsInList = {}
        self.InitUI()

    def InitUI(self):
        """
        main loop of the gui list
        """
        self.server = Server(IP, PORT)
        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.listbox = wx.ListBox(panel)
        hbox.Add(self.listbox, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)

        btnPanel = wx.Panel(panel)
        vbox = wx.BoxSizer(wx.VERTICAL)
        newBtn = wx.Button(btnPanel, wx.ID_ANY, 'New', size=(90, 30))
        renBtn = wx.Button(btnPanel, wx.ID_ANY, 'Release', size=(90, 30))
        delBtn = wx.Button(btnPanel, wx.ID_ANY, 'Delete', size=(90, 30))
        clrBtn = wx.Button(btnPanel, wx.ID_ANY, 'Clear', size=(90, 30))

        self.Bind(wx.EVT_BUTTON, self.NewItem, id=newBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnRelease, id=renBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDelete, id=delBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnClear, id=clrBtn.GetId())
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnRelease)

        vbox.Add((-1, 20))
        vbox.Add(newBtn)
        vbox.Add(renBtn, 0, wx.TOP, 5)
        vbox.Add(delBtn, 0, wx.TOP, 5)
        vbox.Add(clrBtn, 0, wx.TOP, 5)

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)

        self.SetTitle('wx.ListBox')
        self.Centre()

        self.Bind(wx.EVT_TIMER, self.update_list, self.timer)
        self.timer.Start(1000)

    def NewItem(self, event):
        """
        Adds new item to the list
        """
        try:
            text = wx.GetTextFromUser('Enter a new item', 'Insert dialog')
            if text != '':
                self.listbox.Append(text)
        except Exception as msg:
            print(msg)

    def OnRelease(self, event):
        """
        If release button is pressed sends
        a release message to the appropriate
        computer
        """
        try:
            sel = self.listbox.GetSelection()
            while sel == -1:
                sel = self.listbox.GetSelection()
            text = self.listbox.GetString(sel)
            address = ListInterface.convertsIpAndPortStringToTuple(text)
            print(self.server.ipsAndSockets)
            client_socket = self.server.ipsAndSockets[address]
            renamed = text + " released"
            Server.send_response_to_client(RELEASE_REQUEST, client_socket)
            if renamed != '':
                self.listbox.Delete(sel)
                item_id = self.listbox.Insert(renamed, sel)
                self.listbox.SetSelection(item_id)
        except Exception as msg:
            print(msg)

    def keep_Alive(self):
        """
        checks if all connections are still
        open
        """
        text = ''
        index = 0
        tried_to_send = False
        while text != 'end':
            try:
                text = self.listbox.GetString(index)
                address = ListInterface.convertsIpAndPortStringToTuple(text)
                if address != 'disconnected':
                    tried_to_send = True
                    self.server.send_response_to_client(
                        STILL_ALIVE, self.ipsInList[address])
                index += 1
                tried_to_send = False
            except Exception as msg:
                if tried_to_send is True:
                    text += " disconnected"
                    self.listbox.Delete(index)
                    item_id = self.listbox.Insert(text, index)
                    self.listbox.SetSelection(item_id)
                    index += 1
                    tried_to_send = False
                else:
                    text = 'end'

    def OnDelete(self, event):
        """
        removes element from the
        list
        """
        try:
            sel = self.listbox.GetSelection()
            if sel != -1:
                self.listbox.Delete(sel)
        except Exception as msg:
            print(msg)

    def OnClear(self, event):
        """
        removes all the elements from the
        list
        """
        try:
            self.listbox.Clear()
        except Exception as msg:
            print(msg)

    def update_list(self, var):
        """
        Checks if a new computer has been added to the list
        In addition, checks if all connections are still
        open
        """
        try:
            self.keep_Alive()
            for i in self.server.ipsAndSockets:
                if i not in self.ipsInList:
                    self.listbox.Append(str(i))
                    self.ipsInList[i] = self.server.ipsAndSockets[i]
        except Exception as msg:
            print(msg)

    @staticmethod
    def convertsIpAndPortStringToTuple(text):
        """
        converts Ip and port from String to tuple
        """
        try:
            list1 = text.split()
            if len(list1) == 3 and (list1[2] == 'disconnected' or "released"):
                return 'disconnected'
            var = list1[0]
            var2 = list1[1]
            ip = [x for x in var if x.isdigit() or x == '.']
            port = [x for x in var2 if x.isdigit()]
            ip = ''.join(ip)
            port = ''.join(port)
            return ip, int(port)
        except Exception as msg:
            print(msg)
            return 'disconnected'


def main():
    """
    Runs the main loop
    """
    app = wx.App()
    ex = ListInterface(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
