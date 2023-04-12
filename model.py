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

            next_car = None
            if i < len(self.cars) -1:
                next_car = self.cars[i+1]
            distance_to_next_car = 999
            if next_car != None and next_car.position > car.position:
                this_distance = next_car.position - car.position
                if this_distance < distance_to_next_car:
                    distance_to_next_car = this_distance


            distance_to_next_light_signal = 999
            for light_signal in self.light_signals:
                if light_signal.position < car.position:
                    continue
                this_distance = light_signal.position - car.position
                if this_distance < distance_to_next_light_signal and light_signal.state == 0:
                    distance_to_next_light_signal = this_distance

            distance_to_next_obstacle = min(distance_to_next_car, distance_to_next_light_signal)

            car.do_tick(distance_to_next_obstacle)
            if car.position > self.length - 1:
                remove_car_indexes.append(i)

        for i, remove_index in enumerate(remove_car_indexes):
            remove_index -= i
            del self.cars[remove_index]

        for i, light_signal in enumerate(self.light_signals):
            light_signal.do_tick()

        car = self.generator.do_tick()
        if car != None:
            try:
                self.add_car(car)
            except:
                print("traffic jam!")

        self.list = new_list

    def find_next_car_distance(self, car_index):
        # find the distance to the next car from the current car index
        if car_index == len(self.cars) - 1:
            return 999

        next_car = self.cars[car_index+1]
        distance_to_next_car = next_car.position - self.cars[car_index]

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
        for car_iteration in self.cars:
            if car_iteration.position == car.position:
                raise Exception("car at this position already exists")
        self.cars.append(car)
        self.cars.sort(
            key=lambda car: car.position
        )

    def add_light_signal(self, light_signal):
        for light_signal_iteration in self.light_signals:
            if light_signal_iteration.position == light_signal.position:
                raise Exception("light signal at this position already exists")
        self.light_signals.append(light_signal)
        self.light_signals.sort(
            key=lambda light_signal: light_signal.position
        )

    def empty_list(self):
        return [None for _ in range(self.length)]

class Car:
    def __init__(self, speed, max_speed, position):
        self.speed = speed
        self.max_speed = max_speed
        self.position = position

        self.progress = 0

    def do_tick(self, distance_to_next_obstacle):
        keep_distance = 4
        if distance_to_next_obstacle < keep_distance:
            strength = 1+keep_distance - distance_to_next_obstacle
            self.decelerate(strength)
        else:
            self.accelerate()
        self.progress += self.speed
        if self.progress < 100:
            return
        
        # self.progress is over 100
        self.position += int(self.progress // 100)
        self.progress = self.progress % 100

    def accelerate(self):
        if self.speed < self.max_speed:
            self.speed += self.max_speed / 3

    def decelerate(self, strength):
        MAX_STRENGTH = 4
        minus = 0
        if strength == MAX_STRENGTH:
            minus = self.speed
        else:
            minus = self.speed / (3+MAX_STRENGTH-strength)
        self.speed -= minus
        if self.speed < 0:
            self.speed = 0

class CarGenerator:
    def __init__(self, position=0, delay=10, min_speed=50, max_speed=100):
        self.position = position
        self.delay = delay
        self.min_speed = min_speed
        self.max_speed = max_speed

        self.progress = 0

    def do_tick(self):
        if self.progress < self.delay:
            self.progress += 1
            return None

        self.progress = 0

        max_speed = random.randint(self.min_speed, self.max_speed)
        car = Car(
            speed=max_speed / 2,
            max_speed=random.randint(self.min_speed, self.max_speed),
            position=self.position
        )

        return car


class LightSignal:
    def __init__(self, position, red_duration=50, green_duration=30, red_delay=5, state=0):
        self.position = position

        self.red_duration = red_duration
        self.green_duration = green_duration
        self.red_delay = red_delay
        self.state = state

        if self.state == 0:
            self.progress = 10
        else:
            self.progress = 0 

    def do_tick(self):
        if self.state == 1:
            if self.progress >= self.green_duration:
                self.state = 0
                self.progress = 0
    
        elif self.state == 0:
            if self.progress >= self.red_duration:
                self.state = 1
                self.progress = 0

        self.progress += 1

class Model:
    def __init__(self, size):
        self.size = size
    
        self.frame = self.empty_frame(self.size)
        self.border_frame = self.empty_border_frame(self.size)
    
        self.roads = []
        self.intersections = []

    def add_road(self, road):
        for road_iteration in self.roads:
            if road.offset == road_iteration.offset and road.direction == road_iteration.direction:
                raise Exception("road already exists")
        
        if road.offset >= self.size:
            raise Exception("road offset cannot be bigger or equal to size")
        
        if road.offset == 0 or road.offset == self.size - 1:
            raise Exception("road offset cannot be on the edge")

        self.roads.append(road)
        self.calculate_intersection_light_signals()

    def clear_roads(self, direction):
        if direction != "vertical" and direction != "horizontal":
            raise Exception("invalid road direction")
        remove_indexes = []
        for i, road in enumerate(self.roads):
            self.roads[i].cars = []
            if road.direction == direction:
                remove_indexes.append(i)

        for i, remove_index in enumerate(remove_indexes):
            del self.roads[remove_index-i]

        self.calculate_intersection_light_signals()

    def calculate_intersection_light_signals(self):
        self.intersections = []
        vertical_roads_and_indexes = []
        horizontal_roads_and_indexes = []

        for i, road in enumerate(self.roads):
            self.roads[i].light_signals = []
            if road.direction == "horizontal":
                horizontal_roads_and_indexes.append((i, road))
            elif road.direction == "vertical":
                vertical_roads_and_indexes.append((i, road))

        for horizontal_i, horizontal_road in horizontal_roads_and_indexes:
            for vertical_i, vertical_road in vertical_roads_and_indexes:
                intersection_point = (horizontal_road.offset, vertical_road.offset)

                self.roads[vertical_i].add_light_signal(
                    LightSignal(
                        position=intersection_point[0]-1,
                        state=0
                    )
                )

                self.roads[horizontal_i].add_light_signal(
                    LightSignal(
                        position=intersection_point[1]-1,
                        state=1
                    )
                )

    
        for road_index, road in enumerate(self.roads):
            light_signal_remove_indexes = []
            for light_signal_index, light_signal in reversed(list(enumerate(road.light_signals))):
                if light_signal_index == 0:
                    continue
                light_signal = road.light_signals[light_signal_index]
                next_light_signal = road.light_signals[light_signal_index-1]

                light_signal_position_difference = light_signal.position - next_light_signal.position

                if light_signal_position_difference == 2 or light_signal_position_difference == 1:
                    light_signal_remove_indexes.append(light_signal_index)

            if len(light_signal_remove_indexes) == 0:
                continue

            for remove_index in light_signal_remove_indexes:
                del self.roads[road_index].light_signals[remove_index]


            

    def do_tick(self):
        self.frame = self.empty_frame(self.size)
        self.border_frame = self.empty_border_frame(self.size)

        for road in self.roads:
            road.do_tick() # road logic work
            self.do_road(road) # road display work

    def do_road(self, road):
        for light_signal in road.light_signals:
            x = road.offset
            y = light_signal.position
            if road.direction == "vertical":
                x, y = y, x
            
            self.frame[x][y] = light_signal.state + 3
            self.border_frame[x][y] = light_signal.state + 3

        for position in range(road.length):
            car = road.list[position]
            if car is not None:
                if road.direction == "horizontal":
                    self.frame[road.offset][position] = 2 # car
                elif road.direction == "vertical":
                    self.frame[position][road.offset] = 2 # car
            else:
                x = road.offset
                y = position
                if road.direction == "vertical":
                    x, y = y, x

                value = self.frame[x][y]
                if value != 0:
                    continue
                self.frame[x][y] = 1 # empty road

    def empty_frame(self, size):
        frame = [0] * size
        for x in range(size):
            frame[x] = [0] * size

        return frame
    
    def empty_border_frame(self, size):
        frame = [11] * size
        for x in range(size):
            frame[x] = [11] * size

        return frame
