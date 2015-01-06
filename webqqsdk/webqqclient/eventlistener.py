#coding=UTF8

import threading
import time
import traceback
import message

Thread = threading.Thread

class EventListener(Thread):

    def __init__(self,msgs,events,errorHandler):

        super(EventListener,self).__init__()

        self.msgs = msgs
        self.events = events
        self.errorHandler = errorHandler

        self.running = True

    def pause(self):

        self.running = False

    def restore(self):

        self.running = True
    
    def run(self):

        while True:
            if not self.running:
                continue

            if self.msgs:
                msg = self.msgs.pop(0)
                for event in self.events:
                    while msg.paused:pass
                    if msg.isOver:
                        break
                    try:
                        event.main(msg)
                    except Exception,e:
                        msg = message.ErrorMsg()
                        msg.msg = traceback.format_exc()
                        msg.summary = e
                        self.errorHandler(msg)
            time.sleep(0.1)

