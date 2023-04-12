import random

class Road:
    def __init__(self, offset, direction, length, generator):
        if direction  not in ["horizontal",  "vertical"]:
            raise Exception("road direction must be horizontal or vertical")

        self.offset = offset
        self.direction = direction
        self.length = length
        self.generator = generator
        self.list = self.empty_list()
        self.cars = []
        self.light_signals = []

    def do_tick(self):
        # update the state of the road for the current tick
        new_list = self.empty_list()
        remove_car_indexes = []

        # update cars positions
        for i, car in enumerate(self.cars):
            new_list[car.position] = car
            distance_to_next_car = self.find_next_car_distance(i)
            distance_to_next_light_signal = self.find_next_light_signal_distance(car.position)

            # find the closest obstacle (car or light signal)
            distance_to_next_obstacle = min(distance_to_next_car, distance_to_next_light_signal)

            # update car state
            car.do_tick(distance_to_next_obstacle)
            if car.position > self.length - 1:
                remove_car_indexes.append(i)

        # remove cars that have left the road
        for i, remove_index in enumerate(remove_car_indexes):
            del self.cars[remove_index-i]

        # update light signals states
        for light_signal in self.light_signals:
            light_signal.do_tick()

        # generate new car if wanted
        car = self.generator.do_tick()
        if car is not None:
            try:
                self.add_car(car)
            except:
                # car cannot be added
                # --> cars jammed up
                # not an error state
                print("traffic jam!")

        self.list = new_list

    def find_next_car_distance(self, car_index):
        # find the distance to the next car from the current car index
        if car_index == len(self.cars) - 1:
            return 999

        next_car = self.cars[car_index+1]
        distance_to_next_car = next_car.position - self.cars[car_index].position

        return distance_to_next_car
    
    def find_next_light_signal_distance(self, car_position):
        # find the distance to the next light signal from the current car position
        distance_to_next_light_signal = 999
        for light_signal in self.light_signals:
            if light_signal.position < car_position:
                continue
            distance = light_signal.position - car_position
            # check if distance is lower than lowest distance before & check if light is red
            if distance < distance_to_next_light_signal and light_signal.state == 0:
                distance_to_next_light_signal = distance

        return distance_to_next_light_signal

    def add_car(self, car):
        # add a car to the road
        if any(existing_car.position == car.position for existing_car in self.cars):
            raise Exception("car at this position already exists")
        self.cars.append(car)
        # sort cars by position for easier updates
        self.cars.sort(key=lambda car: car.position)

    def add_light_signal(self, light_signal):
        if any(existing_light_signal.position == light_signal.position for existing_light_signal in self.light_signals):
            raise Exception("light signal at this position already exists")
        self.light_signals.append(light_signal)
        self.light_signals.sort(key=lambda light_signal: light_signal.position)

    def empty_list(self):
        # create an empty list for the road's list
        return [None for _ in range(self.length)]

# anything below 4 cells distance between is considered critical and deceleration is needed
DESIRED_CAR_OBSTACLE_DISTANCE = 4
# how fast cars are able to accelerate based on their max speed
# value of 10 = slow acceleration, value of 1 = instant max speed acceleration
ACCELERATION_DIVIDER = 3
# decreases speed of deceleration for more realistic decelerations accounting for
# reaction times and imperfect breaking
DECELERATION_SLOWER = 3
# deceleration strength maximum, arbitrary number
MAX_DECELERATION_STRENGTH = 4

class Car:
    def __init__(self, speed, max_speed, position):
        self.speed = speed
        self.max_speed = max_speed
        self.position = position
        self.progress = 0

    def do_tick(self, distance_to_next_obstacle):
        # update the state of the car for the current tick (frame)
        # do different accelerations/decelerations based on the distance to the next obstacle
        if distance_to_next_obstacle < DESIRED_CAR_OBSTACLE_DISTANCE:
            # calculate deceleration strength based on the distance to the next obstacle
            strength = 1 + DESIRED_CAR_OBSTACLE_DISTANCE - distance_to_next_obstacle
            self.decelerate(strength)
        else:
            # accelerations are constant, distance to next obstacle does not matter
            self.accelerate()

        # keep track of progress, 0-100
        # even if not a whole cell is moved, we want to keep track of the distance moved 
        self.progress += self.speed
        if self.progress < 100:
            return
        
        # self.progress is over 100, add to position and keep rest of progress
        self.position += int(self.progress // 100)
        self.progress = self.progress % 100

    def accelerate(self):
        # increase the cars speed by percentage of max speed based on ACCELERATION_DIVIDER
        if self.speed < self.max_speed:
            self.speed += self.max_speed / ACCELERATION_DIVIDER

    def decelerate(self, strength):
        # decrease the cars speed based on "break strength"
        if strength == MAX_DECELERATION_STRENGTH:
            # full stop on max break strength
            minus = self.speed
        else:
            divisor = DECELERATION_SLOWER + MAX_DECELERATION_STRENGTH - strength
            if divisor <= 0:
                divisor = 1
            minus = self.speed / divisor

        self.speed -= minus
        if self.speed < 0:
            self.speed = 0

class CarGenerator:
    def __init__(self, position=0, delay=10, min_speed=75, max_speed=125):
        self.position = position
        self.delay = delay
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.progress = 0

    def do_tick(self):
        # generate a new car after x ticks delay
        if self.progress < self.delay:
            self.progress += 1
            return None

        self.progress = 0
        # choose random max_speed based on min and max
        max_speed = random.randint(self.min_speed, self.max_speed)
        car = Car(
            # start of with half of the max speed
            speed=max_speed / 2,
            max_speed=max_speed,
            position=self.position
        )

        return car

class LightSignal:
    def __init__(self, position, red_duration=50, green_duration=30, red_delay=5, state=0):
        if red_duration <= green_duration:
            raise Exception("red_duration must be greater than green_duration")
        
        self.position = position
        self.red_duration = red_duration
        self.green_duration = green_duration
        self.red_delay = red_delay
        # state of 0 = red, 1 = green
        self.state = state
        self.progress = 0

        # add an offset so lights stay red
        # avoids crashes, allows other cars on intersections to pass before turning green
        if self.state == 0:
            offset = (red_duration - green_duration) / 2
            self.progress = self.progress + offset

    def do_tick(self):
        # update the state of the light signal
        if self.state == 1 and self.progress >= self.green_duration:
                self.state = 0
                self.progress = 0
    
        elif self.state == 0 and self.progress >= self.red_duration:
                self.state = 1
                self.progress = 0

        self.progress += 1

class Model:
    def __init__(self, size):
        self.size = size
        self.grid = self.empty_grid(self.size)
        self.border_frame = self.empty_border_grid(self.size)
        self.roads = []
        self.intersections = []

    def add_road(self, road):
        # add a road to the model
        for road_iteration in self.roads:
            if road.offset == road_iteration.offset and road.direction == road_iteration.direction:
                raise Exception("road already exists")
        
        if road.offset >= self.size or road.offset in [0, self.size - 1]:
            raise Exception("road offset cannot be on the edge or bigger or equal to size")
        
        self.roads.append(road)
        self.calculate_intersection_light_signals()

    def clear_roads(self, direction):
        # clear all roads in the given direction
        if direction not in ["vertical", "horizontal"]:
            raise Exception("invalid road direction")
        
        self.roads = [road for road in self.roads if road.direction != direction]
        for road in self.roads:
            road.cars = []

        self.calculate_intersection_light_signals()

    def calculate_intersection_light_signals(self):
        # calculate light signales at intersections, clear old light signales
        self.intersections = []
        for road in self.roads:
            road.light_signals = []
        # isolate vertical and horizontal roads
        vertical_roads = [road for road in self.roads if road.direction == "vertical"]
        horizontal_roads = [road for road in self.roads if road.direction == "horizontal"]

        for vertical_road in vertical_roads:
            for horizontal_road in horizontal_roads:
                # find all intersection points (x, y)
                intersection_point = (horizontal_road.offset, vertical_road.offset)

                # add light signal one position before the intersection on both roads
                vertical_road.add_light_signal(
                    LightSignal(
                        # vertical road --> need x position -1
                        position=intersection_point[0] - 1,
                        state = 0
                    )
                )

                horizontal_road.add_light_signal(
                    LightSignal(
                        # horizontal road --> need y position -1
                        position=intersection_point[1] - 1,
                        state=1
                    )
                )

        # if two roads are next to each other, only one light signal is needed
        # we added multiple for intersections next to each other though
        # now, we need to remove all light signals that are directly next to each other
        # or only have one cell distance and are on the same road
        for road in self.roads:
            light_signal_remove_indexes = []
            # loop through the array in reverse order to remove all light signales
            # that have another light signal before themselves
            for light_signal_index, light_signal in reversed(list(enumerate(road.light_signals))):
                if light_signal_index == 0:
                    continue

                previous_light_signal = road.light_signals[light_signal_index - 1]
                light_signales_distance = light_signal.position - previous_light_signal.position
                if light_signales_distance in [1, 2]:
                    light_signal_remove_indexes.append(light_signal_index)

            # can remove them directly, since we reversed the list beforehand
            # --> we have reversed indexes, e.g. [5, 2, 1]
            for remove_index in light_signal_remove_indexes:
                del road.light_signals[remove_index]
            
    def do_tick(self):
        # perform a full tick and update the model
        self.grid = self.empty_grid(self.size)
        self.border_grid = self.empty_border_grid(self.size)

        for road in self.roads:
            road.do_tick() # execute road logic
            self.render_road(road) # render road to the grid

    def update_generators_speed(self, min_speed, max_speed):
        # re-initiate generator in all roads with new min/max speeds
        for road in self.roads:
            road.generator = CarGenerator(
                position=0,
                delay=road.generator.delay,
                min_speed=min_speed,
                max_speed=max_speed
            )

    def update_generators_delay(self, delay):
        # re-initiate generator in all roads with new delay
        for road in self.roads:
            road.generator = CarGenerator(
                position=road.generator.position,
                delay=delay,
                min_speed=road.generator.min_speed,
                max_speed=road.generator.max_speed
            )

    def render_road(self, road):
        # assign the right values to the grid for this road
        for light_signal in road.light_signals:
            # calculate (x, y) based on road direction, offset and light signal position on the riad
            x, y = (road.offset, light_signal.position) if road.direction == "vertical" else (light_signal.position, road.offset)
            
            # red = 0 state, green = 1 state
            # in our color map, the colors are + 3 from our binary light signal state
            self.grid[x][y] = light_signal.state + 3
            self.border_grid[x][y] = light_signal.state + 3

        for position, car in enumerate(road.list):
            # calculate (x, y) like light signal
            x, y = (road.offset, position) if road.direction == "vertical" else (position, road.offset)
            if car is not None:
                self.grid[x][y] = 2 # digit code for blue
            elif self.grid[x][y] == 0: # only set road if cell is not light signal and not car
                self.grid[x][y] = 1 # digit code for empty road

    def empty_grid(self, size):
        # create an empty grid
        grid = [0] * size # 0 = white
        for x in range(size):
            grid[x] = [0] * size

        return grid
    
    def empty_border_grid(self, size):
        # create an empty border grid
        grid = [5] * size # 5 = lightgrey
        for x in range(size):
            grid[x] = [5] * size

        return grid
