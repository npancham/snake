import numpy as np
from snake import Game, Orientation


class Solver(Game):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)
        self.target_queue = []

    def solve(self):
        # If the snake currently does not have a path to follow, determine what path to follow
        if self.target_queue == []:
            self.target_queue = self.determine_path_to_take()

        # If the snake has a path to follow, navigate to the first element in the path
        if self.target_queue != []:
            target_coordinates = self.target_queue.pop(0)
            self.determine_next_move(target_coordinates)

        return self.update()

    def determine_path_to_take(self):
        path = []

        head = self.get_snake_head_coordinates()
        food = self.get_food_coordinates()

        snake_length = len(self.snake.body_coordinates) + 1

        blocked = self.get_currently_blocked_cells()

        path_from_head_to_food = self.calculate_path_between(head, food, blocked)

        # If there exists a path from the snake's head to the food, the snake should take that path only if there exists
        # a path back to the snake's tail after having reached the food. This is important as failing to check this can
        # cause the snake to get trapped by its own body.
        if path_from_head_to_food != []:
            # To avoid needless calculation, the check for an existing path back to snake's tail is only done if the
            # snake's length is not smaller than 2, since in the other case the snake's body is too short to trap
            # itself.
            if snake_length < 2:
                path = path_from_head_to_food
            else:
                blocked_after_reaching_food = self.get_blocked_cells_after_reaching_food(path_from_head_to_food)
                tail = self.get_snake_body_coordinates()[-1]
                path_from_food_to_tail = self.calculate_path_between(food, tail, blocked_after_reaching_food)

                if path_from_food_to_tail != []:
                    path = path_from_head_to_food

                # If there does not exist a path from the food back to the snake's tail, go directly from the current
                # position to the tail instead.
                else:
                    path_from_head_to_tail = self.calculate_path_between(head, tail, blocked[:-1])
                    path = path_from_head_to_tail

        # If there does not exist a path from the snake's head to the food, go to the tail instead.
        else:
            if snake_length > 2:
                tail = self.get_snake_body_coordinates()[-1]
                path_from_head_to_tail = self.calculate_path_between(head, tail, blocked[:-1])
                path = path_from_head_to_tail

        return path

    def calculate_path_between(self, start, goal, blocked):
        dijkstra = Dijkstra(self.grid, start, goal, blocked)
        path = dijkstra.get_path()
        return path

    def get_currently_blocked_cells(self):
        blocked = []

        if self.snake.orientation == Orientation.NORTH:
            previous_cell = self.snake.head_coordinates + np.array([0, 1])
            blocked.append(previous_cell)
        elif self.snake.orientation == Orientation.EAST:
            previous_cell = self.snake.head_coordinates + np.array([-1, 0])
            blocked.append(previous_cell)
        elif self.snake.orientation == Orientation.SOUTH:
            previous_cell = self.snake.head_coordinates + np.array([0, -1])
            blocked.append(previous_cell)
        elif self.snake.orientation == Orientation.WEST:
            previous_cell = self.snake.head_coordinates + np.array([1, 0])
            blocked.append(previous_cell)

        for coordinates in self.snake.body_coordinates:
            blocked.append(coordinates)

        return blocked

    def get_blocked_cells_after_reaching_food(self, path_from_head_to_food):
        snake_length = len(self.snake.body_coordinates) + 1

        snake_head_after_reaching_food = path_from_head_to_food[-1]
        snake_body_after_reaching_food = []

        if snake_length == 1:
            pass
        elif snake_length <= len(path_from_head_to_food):
            # Get the <snake_length - 1> elements in the list before the last element and reverse the order
            snake_body_after_reaching_food = path_from_head_to_food[-snake_length:-1][::-1]
        else:
            # The first <len(path_from_head_to_food) - 1> body coordinates after reaching the food are simply all the
            # coordinates minus the last one in <path_from_head_to_food> in reverse order
            snake_body_after_reaching_food = path_from_head_to_food[:-1][::-1]

            # The remaining body coordinates after reaching the food are the current head coordinates and the first
            # <remaining_elements_to_add - 1> current body coordinates
            remaining_elements_to_add = snake_length - len(path_from_head_to_food)
            snake_body_after_reaching_food.append(self.get_snake_head_coordinates())

            if remaining_elements_to_add > 1:
                for i in range(0, remaining_elements_to_add - 1):
                    snake_body_after_reaching_food.append(self.get_snake_body_coordinates()[i])

        blocked_after_reaching_food = snake_body_after_reaching_food

        return blocked_after_reaching_food

    def determine_next_move(self, target_coordinates):
        head_coordinates = self.snake.head_coordinates
        delta_coordinates = target_coordinates - head_coordinates

        if delta_coordinates[1] == -1:
            self.snake_go_north()
        elif delta_coordinates[0] == 1:
            self.snake_go_east()
        elif delta_coordinates[1] == 1:
            self.snake_go_south()
        elif delta_coordinates[0] == -1:
            self.snake_go_west()


class Dijkstra:
    def __init__(self, grid, start, goal, blocked):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.blocked = blocked
        self.unvisited = set()
        self.values = dict()
        self.path = None
        self.UNREACHABLE_VALUE = self.grid.rows * self.grid.columns

        self.calculate_values()
        self.calculate_path()

    def calculate_values(self):
        # Add all cells to the unvisited set and initialize all cells with a value of infinity (i.e. value currently
        # unknown)
        for i in range(self.grid.rows * self.grid.columns):
            self.unvisited.add(i)
            self.values.update({i: np.inf})

        # Set the value of the start cell to 0
        self.values.update({self.grid.coordinates_to_index(self.start): 0})

        current = self.start

        # Loop until the goal cell is visited:
        while self.grid.coordinates_to_index(self.goal) in self.unvisited:
            self.update_neighbor_values(current)
            self.unvisited.remove(self.grid.coordinates_to_index(current))

            # Get a subset of the values dictionary only consisting of the key-value pairs of unvisited cells
            unvisited_values = dict((key, self.values[key]) for key in list(self.unvisited) if key in self.values)

            if unvisited_values != {}:
                # The current cell for the next iteration is the one with the lowest value
                current = self.grid.index_to_coordinates(min(unvisited_values, key=unvisited_values.get))

    def get_value(self, coordinates):
        if coordinates[0] < 0 or coordinates[1] < 0 or coordinates[0] >= self.grid.columns or coordinates[1] >= self.grid.rows:
            return None

        index = self.grid.coordinates_to_index(coordinates)
        value = self.values[index]

        return value

    def set_value(self, coordinates, value):
        if coordinates[0] < 0 or coordinates[1] < 0 or coordinates[0] >= self.grid.columns or coordinates[1] >= self.grid.rows:
            return

        index = self.grid.coordinates_to_index(coordinates)
        self.values.update({index: value})

    def update_neighbor_values(self, current):
        north = current + np.array([0, -1])
        east = current + np.array([1, 0])
        south = current + np.array([0, 1])
        west = current + np.array([-1, 0])

        north_index = self.grid.coordinates_to_index(north)
        east_index = self.grid.coordinates_to_index(east)
        south_index = self.grid.coordinates_to_index(south)
        west_index = self.grid.coordinates_to_index(west)

        current_value = self.get_value(current)

        if north_index in self.unvisited:
            # If north is a blocked cell:
            if np.any(np.all(north == self.blocked, axis=1)):
                self.set_value(north, self.UNREACHABLE_VALUE)
            elif current_value + 1 < self.get_value(north):
                self.set_value(north, current_value + 1)

        if east_index in self.unvisited:
            # If east is a blocked cell:
            if np.any(np.all(east == self.blocked, axis=1)):
                self.set_value(east, self.UNREACHABLE_VALUE)
            elif current_value + 1 < self.get_value(east):
                self.set_value(east, current_value + 1)

        if south_index in self.unvisited:
            # If south is a blocked cell:
            if np.any(np.all(south == self.blocked, axis=1)):
                self.set_value(south, self.UNREACHABLE_VALUE)
            elif current_value + 1 < self.get_value(south):
                self.set_value(south, current_value + 1)

        if west_index in self.unvisited:
            # If west is a blocked cell:
            if np.any(np.all(west == self.blocked, axis=1)):
                self.set_value(west, self.UNREACHABLE_VALUE)
            elif current_value + 1 < self.get_value(west):
                self.set_value(west, current_value + 1)

    def get_lowest_valued_neighbor(self, current):
        north = current + np.array([0, -1])
        east = current + np.array([1, 0])
        south = current + np.array([0, 1])
        west = current + np.array([-1, 0])

        current_value = self.get_value(current)
        north_value = self.get_value(north)
        east_value = self.get_value(east)
        south_value = self.get_value(south)
        west_value = self.get_value(west)

        lowest_neighbors = []

        if north_value is not None and north_value < current_value:
            lowest_neighbors.append(north)

        if east_value is not None and east_value < current_value:
            lowest_neighbors.append(east)

        if south_value is not None and south_value < current_value:
            lowest_neighbors.append(south)

        if west_value is not None and west_value < current_value:
            lowest_neighbors.append(west)

        return lowest_neighbors[0]
        # Since the first element in lowest_neighbors is returned and the elements in lowest_neighbors have a specific
        # order, the path that is eventually created by the invoker of this function has a bias of always going in one
        # direction first (e.g. if the start is in the top-left corner and the goal is in the bottom-right corner, the
        # path that is created will always go from top-left to top-right to bottom-right, and never from top-left to
        # bottom-left to bottom-right). This is still better than choosing a random element from lowest_neighbors, as
        # that would create zigzag patterns. Ideally, all shortest path are calculated and the best one is chosen based
        # on the state of the snake, but this will require more computational resources for every run of the algorithm.

    def calculate_path(self):
        # Dijkstra's algorithm generally results in multiple paths all being the shortest. However, for computational
        # efficiency, only one shortest path is calculated.
        start = self.start
        goal = self.goal
        path = []
        goal_value = self.get_value(goal)

        # Calculating a path is only possible when the goal is reachable
        if goal_value < self.UNREACHABLE_VALUE:
            current = goal

            while not np.array_equal(current, start):
                path.insert(0, current)
                current = self.get_lowest_valued_neighbor(current)

        self.path = path

    def get_path(self):
        return self.path
