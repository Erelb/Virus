# The Virus

Virus and antivirus. The virus paralyzes the computer it is running on. This project is done using a client-server model, and the communication is done using sockets.

## Project definition

The model I used in the project is a server and client model, the blocked computer in this case is the client, and in addition to it, there is the central server.

#### The blocked computer side

The algorithm of the virus code is divided into three parts: blocking the keyboard and mouse through python libraries, removing the options from the cad screen using the registry through python, and transplanting and creating a connection with the main server.

The transplant:

The user runs a Pacman game that was sent to him in a python.exe file.
After that, a thread is started that creates the connection with the server, and downloads the virus file. The file goes in parts of 1024 bits each and is written in the folder - startup_directory: a folder where the saved files come up when the computer is restarted. After connecting to the server and creating the file, the thread runs the virus file.
Activation of the virus:
The virus file creates and starts a thread responsible for connecting with the central server, so if necessary the virus will receive a release message, cancel all its effects and stop running.
After establishing a connection with the server, the virus file deletes the control alt delete options through the registry:
It uses the _winreg library - a package that wraps the Windows API through which you can read values ​​from the registry, change and add. To download the options from the CAD screen we will add values ​​to the folders -
 HKEY_LOCAL_MACHINE - stores specific settings for the local computer. Through this folder, we will block the computer's task manager option, and the option to change user.
HKEY_CURRENT_USER – stores settings related to the specific connected user. Through this folder we will block the options: change password, disconnect from the user, and lock.

In addition, the virus file will block the keyboard keys - using the keyboard library, and create another thread, which will take over the mouse and place it in the corner of the screen without being able to move using the mouse library. Finally, the program will open a black GUI window, without the X button, that will be spread over the entire screen.

After the program receives a "release" message from the central server, it will close the thread that blocks the mouse, return the keyboard keys to work, return the options to the control alt delete screen and remove the black screen.

#### The main server computer
The central server has a list GUI interface, and for this, I used the wx library. The list has different buttons and features, and through it, the user of the virus manages it. The list is constantly updated and maintains a connection with its computers.
In the InitUi loop, in addition to initializing the list, the server is initialized.

#### The antivirus file - in the file system 
The purpose of the antivirus file is to prevent adding an unwanted file to the startupdirectory folder. Watchdog: A Python class that works with a Windows API that reports events in the computer's file system. Every time a new file is created, a file is changed or a file is deleted in a watched folder, the event is passed to the event manager function. To receive updates on the changes in the desired folder, the antivirus file uses a watchdog. When an update is received about the creation of a new python file, the antivirus pops up a message to the user and asks him if he wants to delete the created file. If the user approves, the virus file is deleted, and the virus is stopped.

#### The antivirus file - registry
 To receive updates on changes made to the registry files - an antivirus file uses win32api. 
 Win32api: In Python, a library that contains all the operations, types, and services that the operating system exports to programs. This library is a shell for HighLevel languages. The antivirus file creates several threads. Each thread sits in a different folder in the registry and every time an update is received about a change in that folder, it goes through the entries in the folder. If a harmful value is found (harmful to controlAltDelete), it pops a message on the screen and asks the user if he wants to delete the value. If the user approves all the messages, the options on the cad screen are not affected.
 
 
## Setup
To run the game (which contains the virus file), PIP must be installed on the computer, and the "freegames" library must be downloaded.
