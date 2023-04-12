from tkinter import *
import time

from view import *
from model import *

# tick delay in ms
# 50 --> approx. 20 FPS
TICK_DELAY = 50

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
            handle_set_num_roads=self.handle_set_num_roads,
            handle_set_generator_avg_speed=self.handle_set_generator_avg_speed,
            handle_set_generator_delay=self.handle_set_generator_delay
        )
        self.model = Model(size=self.size)

        self.is_running = False

        self.handle_set_num_roads(1, "horizontal")
        self.handle_set_num_roads(1, "vertical")

        self.do_tick()

    def handle_tick(self):
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
                    # exception arises if offset is already used
                    # try again with new random value
                    pass

        self.do_tick()

    def handle_set_generator_avg_speed(self, avg_speed):
        min_speed = int(avg_speed - (avg_speed / 4))
        max_speed = int(avg_speed + (avg_speed / 4))

        self.model.update_generators_speed(min_speed, max_speed)

    def handle_set_generator_delay(self, delay):
        self.model.update_generators_delay(delay)

    def tick_loop(self):
        # check if should still be running
        if not self.is_running:
            return
        
        self.do_tick()
        self.root.after(TICK_DELAY, self.tick_loop)

    def do_tick(self):
        self.model.do_tick()
        self.view.draw_frame(self.model.grid, self.model.border_grid)

    def mainloop(self):
        self.root.mainloop()
