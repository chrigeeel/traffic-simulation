from tkinter import *
import time

from view import *
from model import *

class Controller:
    def __init__(self, root, size=50):
        self.root = root
        self.size = size
        self.view = View(
            self.root,
            size=self.size,
            handle_tick=self.handle_tick,
            handle_start=self.handle_start,
            handle_stop=self.handle_stop,
            handle_set_num_roads=self.handle_set_num_roads
        )
        self.model = Model(size=self.size)

        self.is_running = False

        self.do_tick()

    def handle_start(self):
        if self.is_running:
            raise Exception("already running")
        self.is_running = True

        self.tick_loop()

    def handle_stop(self):
        if not self.is_running:
            raise Exception("not running")
        
        self.is_running = False
        
    def handle_tick(self):
        self.do_tick()

    def handle_set_num_roads(self, num_roads, direction):
        self.model.clear_roads(direction)
        for _ in range(num_roads):
            while True:
                try:
                    self.model.add_road(
                        Road(
                            offset=random.randint(1, self.size-2),
                            direction=direction,
                            length=self.size,
                            generator=CarGenerator()
                        )
                    )
                    break
                except:
                    pass

        self.do_tick()

    def tick_loop(self, delay=50):
        # check if should still be running
        if not self.is_running:
            return
        
        self.do_tick()
        self.root.after(delay, self.tick_loop)

    def do_tick(self):
        self.model.do_tick()
        self.view.draw_frame(self.model.frame, self.model.border_frame)

    def mainloop(self):
        self.root.mainloop()
