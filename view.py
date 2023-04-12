from tkinter import *
import time

COLOR_MAP = {
    0: "white", # empty cell
    1: "black", # road
    2: "blue", # car
    3: "red",
    4: "green",
    9: "yellow", # car generator
    11: "lightgrey", # border
}

SIMULATION_SIZE = 500

class View:
    def __init__(
            self, 
            root, 
            size,
            handle_tick,
            handle_start, 
            handle_stop, 
            handle_set_num_roads
        ):
        self.cell_size = int(SIMULATION_SIZE / size)

        print(self.cell_size)

        self.root = root

        self.width = SIMULATION_SIZE
        self.height = SIMULATION_SIZE

        self.raster = Canvas(self.root, width=self.width, height=self.height)
        self.raster.grid(row=0, column=0, columnspan=3)

        # handlers
        self.handle_start = handle_start
        self.handle_tick = handle_tick
        self.handle_stop = handle_stop
        self.handle_set_num_roads = handle_set_num_roads

        self.b_tick = Button(
            self.root,
            text="Tick",
            command=handle_tick
        )
        self.b_tick.grid(row=1, column=0)
        
        self.b_start = Button(
            self.root,
            text="Start",
            command=self.handle_start,
        )
        self.b_start.grid(row=1, column=1)

        self.b_stop = Button(
            self.root,
            text="Stop",
            command=self.handle_stop,
        )
        self.b_stop.grid(row=1, column=2)

        self.num_vertical_roads = IntVar()
        self.s_num_vertical_roads = Scale(
            self.root,
            from_=0,
            to=10,
            relief=GROOVE,
            orient=HORIZONTAL,
            variable=self.num_vertical_roads,
            command=lambda _ : self.handle_set_num_roads(self.num_vertical_roads.get(), "vertical")
        )
        self.s_num_vertical_roads.grid(row=2, column=0)

        self.num_horizontal_roads = IntVar()
        self.s_num_horizontal_roads = Scale(
            self.root,
            from_=0,
            to=10,
            relief=GROOVE,
            orient=HORIZONTAL,
            variable=self.num_horizontal_roads,
            command=lambda _ : self.handle_set_num_roads(self.num_horizontal_roads.get(), "horizontal")
        )
        self.s_num_horizontal_roads.grid(row=2, column=1)

    def draw_frame(self, frame, border_frame):
        self.raster.delete(ALL)
        for x, row in enumerate(frame):
            for y, value in enumerate(row):
                self.draw_cell(x, y, COLOR_MAP[value], COLOR_MAP[border_frame[x][y]])
                               

    def draw_cell(self, x, y, color, border):
        self.raster.create_rectangle(
            x*self.cell_size,
            y*self.cell_size,
            x*self.cell_size + self.cell_size,
            y*self.cell_size + self.cell_size,
            fill=color,
            outline=border,
            width=self.cell_size / 10
        )