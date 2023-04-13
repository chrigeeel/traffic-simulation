"""
Description: A simulation environment for car traffic with cellular automata
The program encapsules four files: main.py, controller.py, model.py, view.py
Author: Christian Tognazza
Datum: 13.04.2023
"""

from tkinter import *

from view import *
from model import *

# tick delay in ms
# TICK DELAY 50 --> approx. 1000/50 = 20 FPS
TICK_DELAY = 50

# Controller class that handles the interaction between the Model and View


class Controller:
    def __init__(self, root, size=50):
        self.root = root
        self.size = size

        # initialize the view and model
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

    # method to handle ticks, which update the model and view
    def handle_tick(self):
        self.do_tick()

    # method to start the simulation
    def handle_start(self):
        if self.is_running:
            print("already running")
            return
            #raise Exception("already running")

        self.is_running = True

        self.tick_loop()

    # method to stop the simulation
    def handle_stop(self):
        if not self.is_running:
            print("not running")
            return
            #raise Exception("not running")

        self.is_running = False

    # method to handle the number of roads in the simulation
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

    # method to handle the average speed of car generators
    def handle_set_generator_avg_speed(self, avg_speed):
        min_speed = int(avg_speed - (avg_speed / 4))
        max_speed = int(avg_speed + (avg_speed / 4))

        self.model.update_generators_speed(min_speed, max_speed)

    # method to handle the delay of car generators
    def handle_set_generator_delay(self, delay):
        self.model.update_generators_delay(delay)

    # main loop for ticks when the simulation is running
    def tick_loop(self):
        # check if should still be running
        if not self.is_running:
            return

        self.do_tick()
        self.root.after(TICK_DELAY, self.tick_loop)

    # nethod to perform a single tick, updating the model and view
    def do_tick(self):
        self.model.do_tick()
        self.view.draw_grid(self.model.grid, self.model.border_grid)

    # start the main loop of the tkinter application
    def mainloop(self):
        self.root.mainloop()
