# Client Introduction

The DisGraFS Client is called by the web UI and performs the following tasks: 

- Automatically mounts JuiceFS
- Receives and executes commands from the web UI via Websockets
  - Delete a certain file in JuiceFS
  - Exit
- Monitors any file operations in JuiceFS with Watchdog and reports it to the web UI via Websockets
  - File creation
  - File modification
  - File deletion

DisGraFS provides clients for two platforms: Windows 10 and Ubuntu (may also work for other linux distributions, not tested). The main logic in these two versions `DisGraFS-Client.py` are alike but not identical, due to some platform differences. The JuiceFS Client executable, which is to be called by `DisGraFS-Client.py`, also differ on the two platforms. 

To install the client, place the folder in a safe place, (install WinFsp first for windows, ) and run `setup.bat` for Windows or `setup.sh` for linux. 

To know more about other files in the client folder, please refer to `DevNotes.md` in debug version of the client. 

