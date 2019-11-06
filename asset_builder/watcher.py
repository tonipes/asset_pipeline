import sys
import time
import logging
from threading import Lock

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

def what(e):
    return 'directory' if e.is_directory else 'file'
    
class EventHandler(FileSystemEventHandler):    
    def __init__(self, *args, **kwargs):
        super(EventHandler, self).__init__(*args, **kwargs)
        self.changes = []
        self.lock = Lock()

    def add_change(self, path):
        self.lock.acquire()
        self.changes.append(path)
        self.lock.release()

    def get_changed_batch(self):
        res = []

        self.lock.acquire()

        res = list(set(self.changes))

        self.changes.clear()

        self.lock.release()

        return res

    def on_moved(self, event):
        super(EventHandler, self).on_moved(event)

        self.add_change(event.dest_path)

    def on_created(self, event):
        super(EventHandler, self).on_created(event)

        self.add_change(event.src_path)

    def on_deleted(self, event):
        super(EventHandler, self).on_deleted(event)

    def on_modified(self, event):
        super(EventHandler, self).on_modified(event)
        
        self.add_change(event.src_path)


class Watcher(object):
    def __init__(self, builder, batch_callback, delay):
        self.builder = builder
        self.batch_callback = batch_callback
        self.delay = delay
        self.event_handler = EventHandler()
        self.observer = Observer()

    def watch(self, path):
        self.observer.schedule(self.event_handler, path, recursive=True)

        self.observer.start()
        
        try:
            while True:
                time.sleep(self.delay)
                batch = self.event_handler.get_changed_batch()
                
                if batch:
                    modified_outputs = self.builder.build(batch)
                    if modified_outputs:
                        self.batch_callback(modified_outputs)

        except KeyboardInterrupt:
            self.observer.stop()
            
        self.observer.join()
