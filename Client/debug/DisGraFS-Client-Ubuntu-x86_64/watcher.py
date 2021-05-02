import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

def on_created(event):
    message = "Watchdog: "
    if not event.is_directory:
        message = "file "
        message += f"{event.src_path} created"
        print(message)

def on_deleted(event):
    message = "Watchdog: "
    if not event.is_directory:
        message = "file "
        message += f"{event.src_path} deleted"
        print(message)

def on_modified(event):
    message = "Watchdog: "
    if not event.is_directory:
        message = "file "
        message += f"{event.src_path} modified"
        print(message)

def on_moved(event):
    message = "Watchdog: "
    if not event.is_directory:
        message = "file "
        message += f"{event.src_path} moved to {event.dest_path}"
        print(message)

event_handler = FileSystemEventHandler()
event_handler.on_created = on_created
event_handler.on_deleted = on_deleted
event_handler.on_modified = on_modified
event_handler.on_moved = on_moved
my_observer = Observer()
my_observer.schedule(event_handler, "/home/hurrypeng/jfs/", recursive=True)
my_observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass