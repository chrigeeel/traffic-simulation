from tkinter import *

# color map for rendering
# need to be tkinter-compatible colors.
COLOR_MAP = {
    0: "white",  # empty cell
    1: "black",  # road
    2: "blue",  # car
    3: "red",  # light signal
    4: "green",  # light signal
    5: "lightgrey",  # border
}

# size of the simulation canvas
# should not be changed
SIMULATION_SIZE = 500

# View class manages the graphical user interface (GUI)
class View:
    def __init__(
            self, 
            root, 
            size,
            handle_tick,
            handle_start, 
            handle_stop, 
            handle_set_num_roads,
            handle_set_generator_avg_speed,
            handle_set_generator_delay,
        ):
        # configure the root window
        root.minsize(SIMULATION_SIZE, SIMULATION_SIZE + 170)
        self.root = root
        self.cell_size = int(SIMULATION_SIZE / size)
        root.title("Christian Traffic Simulation")

        self.width = SIMULATION_SIZE
        self.height = SIMULATION_SIZE

        # create the canvas for drawing
        self.raster = Canvas(self.root, width=self.width, height=self.height)
        self.raster.grid(row=0, column=0, columnspan=3)

        # set up handler functions for various events
        self.handle_start = handle_start
        self.handle_tick = handle_tick
        self.handle_stop = handle_stop
        self.handle_set_num_roads = handle_set_num_roads
        self.handle_set_generator_avg_speed = handle_set_generator_avg_speed
        self.handle_set_generator_delay = handle_set_generator_delay

        # create and set up the "Execute Tick" button
        self.b_tick = Button(
            self.root,
            text="Execute Tick",
            command=handle_tick
        )
        self.b_tick.grid(row=1, column=0)

        # create and set up the "Start Simulation" button
        self.b_start = Button(
            self.root,
            text="Start Simulation",
            command=self.handle_start,
        )
        self.b_start.grid(row=1, column=1)

        # create and set up the "Stop Simulation" button
        self.b_stop = Button(
            self.root,
            text="Stop Simulation",
            command=self.handle_stop,
        )
        self.b_stop.grid(row=1, column=2)

        # create and set up the label and slider for the number of vertical roads
        self.l_num_vertical_roads = Label(
            self.root,
            text="# Vertical Roads"
        )
        self.l_num_vertical_roads.grid(row=2, column=0)
        self.num_vertical_roads = IntVar()
        self.num_vertical_roads.set(1)
        self.s_num_vertical_roads = Scale(
            self.root,
            from_=0,
            to=10,
            relief=GROOVE,
            orient=HORIZONTAL,
            variable=self.num_vertical_roads,
            command=lambda _ : self.handle_set_num_roads(self.num_vertical_roads.get(), "vertical")
        )
        self.s_num_vertical_roads.grid(row=3, column=0)

        # create and set up the label and slider for the number of horizontal roads
        self.l_num_horizontal_roads = Label(
            self.root,
            text="# Horizontal Roads"
        )
        self.l_num_horizontal_roads.grid(row=2, column=1)
        self.num_horizontal_roads = IntVar()
        self.num_horizontal_roads.set(1)
        self.s_num_horizontal_roads = Scale(
            self.root,
            from_=0,
            to=10,
            relief=GROOVE,
            orient=HORIZONTAL,
            variable=self.num_horizontal_roads,
            command=lambda _ : self.handle_set_num_roads(self.num_horizontal_roads.get(), "horizontal")
        )
        self.s_num_horizontal_roads.grid(row=3, column=1)

        # create and set up the label and slider for the average car speed
        self.l_generator_avg_speed = Label(
            self.root,
            text="Average Car Speed"
        )
        self.l_generator_avg_speed.grid(row=4, column=0)
        self.generator_avg_speed = IntVar()
        self.generator_avg_speed.set(100)
        self.s_generator_avg_speed = Scale(
            self.root,
            from_=50,
            to=200,
            relief=GROOVE,
            orient=HORIZONTAL,
            variable=self.generator_avg_speed,
            command=lambda _ : self.handle_set_generator_avg_speed(self.generator_avg_speed.get())
        )
        self.s_generator_avg_speed.grid(row=5, column=0)

        # create and set up the label and slider for the car generator delay
        self.l_generator_delay = Label(
            self.root,
            text="Car Generator Delay"
        )
        self.l_generator_delay.grid(row=4, column=1)
        self.generator_delay = IntVar()
        self.generator_delay.set(10)
        self.s_generator_delay = Scale(
            self.root,
            from_=3,
            to=30,
            relief=GROOVE,
            orient=HORIZONTAL,
            variable=self.generator_delay,
            command=lambda _ : self.handle_set_generator_delay(self.generator_delay.get())
        )
        self.s_generator_delay.grid(row=5, column=1)

    # draw a grid on the canvas
    def draw_grid(self, grid, border_grid):
        self.raster.delete(ALL)
        for x, row in enumerate(grid):
            for y, value in enumerate(row):
                self.draw_cell(x, y, COLOR_MAP[value], COLOR_MAP[border_grid[x][y]])
                               

    # draw a single cell on the canvas
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