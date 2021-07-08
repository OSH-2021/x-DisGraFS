import os
import sys
import time
import urllib.parse
import subprocess
import websockets
import asyncio
import time
import webbrowser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler
from collections import deque

def extractArgsFromUrl(url):
    args = urllib.parse.unquote(url)
    protocolIndex = args.find("://")
    if protocolIndex == -1:
        print("Error: Wrong url argument format \n")
        input("Press Enter to quit")
        sys.exit(-2)
    args = args[protocolIndex + 3:]
    args = args.split(' ')
    return args

if __name__ == "__main__":

    ########
    # init #
    ########

    print("DisGraFS Client")

    if len(sys.argv) < 2:
        print("Error: Wrong argument format \n")
        input("Press Enter to quit")
        sys.exit(-1)
    cwd = sys.argv[0]
    args = extractArgsFromUrl(sys.argv[1])

    cwd = cwd[:len(cwd) - len("DisGraFS-Client.py")]
    redisUrl = "redis://:disgrafs@juicefs.disgrafs.tech"
    mountPointNoSlash = "/home/hurrypeng/jfs"
    mountPointSlash = "/home/hurrypeng/jfs/"
    wsUrl = "ws://localhost:9090"
    waAuth = "admin:123456"

    try:
        redisUrl = args[0]
        mountPoint = args[1]
        wsUrl = args[2]
        wsAuth = args[3]
        # example: disgrafs://redis://:disgrafs@juicefs.disgrafs.tech /home/hurrypeng/jfs ws://localhost:9090 admin:123456
        if mountPoint[-1] != '/':
            mountPointNoSlash = mountPoint
            mountPointSlash = mountPoint + '/'
        else:
            mountPointNoSlash = mountPoint[:-1]
            mountPointSlash = mountPoint
    except Exception:
        print("Error: Wrong url argument number \n")
        input("Press Enter to quit")
        sys.exit(-3)

    if os.path.exists(mountPointSlash):
        os.rmdir(mountPointSlash)

    print("Starting juicefs...")
    print([cwd + "juicefs", "-q", "mount", redisUrl, mountPointNoSlash])
    subprocess.Popen("sudo " + cwd + "juicefs -q mount " + redisUrl + ' ' + mountPointNoSlash, shell=True)
    print("Juicefs started")

    ############
    # watchdog #
    ############

    def createDatapack(type, path1 : str, path2 = ""):
        timeStamp = int(round(time.time() * 1000))
        purePath1 = path1[len(mountPointSlash):]
        purePath1 = purePath1.replace('\\', '/')
        purePath2 = ""
        if path2 != "":
            purePath2 = path2[len(mountPointSlash):]
            purePath2 = purePath2.replace('\\', '/')
        dictObj = { "type": type, "path1": purePath1, "path2": purePath2, "time":timeStamp }
        return repr(dictObj)

    sendTasklist = deque()

    print("Establishing watchdog observer...")

    def on_created(event):
        message = "Watchdog: "
        if not event.is_directory:
            message = "file "
            message += f"{event.src_path} created"
            print(message)
            sendTasklist.append(createDatapack("create", event.src_path))

    def on_deleted(event):
        message = "Watchdog: "
        if not event.is_directory:
            message = "file "
            message += f"{event.src_path} deleted"
            print(message)
            sendTasklist.append(createDatapack("delete", event.src_path))

    def on_modified(event):
        message = "Watchdog: "
        if not event.is_directory:
            message = "file "
            message += f"{event.src_path} modified"
            print(message)
            sendTasklist.append(createDatapack("modify", event.src_path))

    def on_moved(event):
        message = "Watchdog: "
        if not event.is_directory:
            message = "file "
            message += f"{event.src_path} moved to {event.dest_path}"
            print(message)
            sendTasklist.append(createDatapack("move", event.src_path, event.dest_path))

    event_handler = FileSystemEventHandler()
    event_handler.on_created = on_created
    event_handler.on_deleted = on_deleted
    event_handler.on_modified = on_modified
    event_handler.on_moved = on_moved
    my_observer = Observer()
    print("mpslsh", mountPointSlash)
    while not os.path.exists(mountPointSlash):
        time.sleep(0.1)
    time.sleep(1) # must wait for juicefs to finish mounting
    my_observer.schedule(event_handler, mountPointSlash, recursive=True)
    my_observer.start()
    print("Watchdog observer established")

    async def login():
        wsClient = await websockets.connect(wsUrl)
        await wsClient.send(wsAuth)
        return wsClient

    async def wsSender(wsClient):
        while True:
            while len(sendTasklist) == 0:
                await asyncio.sleep(0.1)
            await wsClient.send(sendTasklist.popleft())

    async def wsReceiver(wsClient):
        while True:
            socketRecv = await wsClient.recv()
            try:
                command = eval(socketRecv)
                if command["command"] == "exit":
                    asyncio.get_event_loop().stop()
                    return
                elif command["command"] == "open":
                    webbrowser.open("file://" + mountPointSlash + command["parameter"][0])
                elif command["command"] == "delete":
                    os.remove(mountPointSlash + command["parameter"][0])
                else:
                    print("Error: Failed to resolve command from server:", socketRecv)
            except Exception:
                print("Error: Failed to execute command from server:", socketRecv)

    try:
        loop = asyncio.get_event_loop()
        wsClient = loop.run_until_complete(login())
        loop.run_until_complete(asyncio.wait([wsSender(wsClient), wsReceiver(wsClient)]))

    except KeyboardInterrupt:
        pass

    finally:
        my_observer.stop()
        subprocess.Popen("juicefs umount " + mountPointNoSlash).wait()
        loop.call_soon(wsClient.close())
        input("Press Enter to quit")
        sys.exit(0)
