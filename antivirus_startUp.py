"""
Anti-virus for the start up
directory
"""
import win32api
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import ctypes
import win32con


# constants
STARTUP_DIRECTORY = "C:\\" \
    "Users\\" \
    "%s\\AppData\\" \
    "Roaming\\Microsoft\\" \
    "Windows\\" \
    "Start Menu\\Programs\\Startup" \
                    % win32api.GetUserName()


class OnMyWatch:
    """
    Set the directory on watch
    """
    watchDirectory = STARTUP_DIRECTORY

    def __init__(self):
        """
        constructor
        """
        self.observer = Observer()

    def run(self):
        """
        Creates the handle object and
        starts to observe
        """
        event_handler = Handler()
        self.observer.schedule(
            event_handler,
            self.watchDirectory,
            recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except BaseException:
            self.observer.stop()
            print("Observer Stopped")
        self.observer.join()


class Handler(FileSystemEventHandler):
    """
    Handles the events
    """

    @staticmethod
    def on_any_event(event):
        """
        Notices if file was created and checks
        if to remove
        """
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Event is created, you can process it now
            print("Watchdog received created event - % s." % event.src_path)
            file_location = event.src_path.split('\\')
            MessageBox = ctypes.windll.user32.MessageBoxW
            yes_no = MessageBox(None,
                                'A file named: ' +
                                str(file_location[-1]) +
                                ' was created, do yo want to remove it? ',
                                'Message',
                                win32con.MB_YESNO)
            if yes_no:
                os.remove(event.src_path)
        elif event.event_type == 'modified':
            # Event is modified, you can process it now
            print("Watchdog received modified event - % s." % event.src_path)


def main():
    """
    Notice if there is a detrimental value that was added
    to the watched folders and enables to remove it
    """
    watch = OnMyWatch()
    watch.run()


if __name__ == '__main__':
    main()