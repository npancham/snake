from enum import Enum
import numpy as np
import random


class Orientation(Enum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4


class Snake:
    def __init__(self):
        self.head_coordinates = np.empty([2])
        self.head_coordinates_previous = np.empty_like(self.head_coordinates)
        self.body_coordinates = []
        self.body_coordinates_previous = []
        self.orientation = Orientation.NORTH
        self.has_eaten_food = False

    def set_orientation(self, orientation):
        self.orientation = orientation

    def set_head_coordinates(self, coordinates):
        self.head_coordinates = coordinates

    def update_position(self):
        self.head_coordinates_previous = np.copy(self.head_coordinates)
        self.body_coordinates_previous = np.copy(self.body_coordinates)

        match self.orientation:
            case Orientation.NORTH:
                self.head_coordinates = self.head_coordinates + np.array([0, -1])
            case Orientation.EAST:
                self.head_coordinates = self.head_coordinates + np.array([1, 0])
            case Orientation.SOUTH:
                self.head_coordinates = self.head_coordinates + np.array([0, 1])
            case Orientation.WEST:
                self.head_coordinates = self.head_coordinates + np.array([-1, 0])

        for i in range(len(self.body_coordinates)):
            if i == 0:
                self.body_coordinates[i] = self.head_coordinates_previous
            else:
                self.body_coordinates[i] = self.body_coordinates_previous[i - 1]

    def eat_food(self):
        self.has_eaten_food = True

    def grow(self):
        if len(self.body_coordinates_previous) == 0:
            self.body_coordinates.append(self.head_coordinates_previous)
        else:
            self.body_coordinates.append(self.body_coordinates_previous[-1])

        self.has_eaten_food = False


class Food:
    def __init__(self):
        self.coordinates = np.empty([1, 2])

    def set_coordinates(self, coordinates):
        self.coordinates = coordinates


class Grid:
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns


class Game:
    def __init__(self, rows, columns):
        self.grid = Grid(rows, columns)
        self.snake = Snake()
        self.food = Food()
        self.score = 0

        self.spawn_snake()
        self.respawn_food()

    def get_snake_head_coordinates(self):
        return self.snake.head_coordinates

    def get_snake_body_coordinates(self):
        return self.snake.body_coordinates

    def get_food_coordinates(self):
        return self.food.coordinates

    def get_score(self):
        return self.score

    def spawn_snake(self):
        empty_cells = self.get_empty_cells()
        chosen_cell = random.choice(empty_cells)
        self.snake.set_head_coordinates(chosen_cell)

        starting_orientations = []

        # Randomly select a starting orientation, while also keeping in mind that the snake must be a certain number of
        # cells away from the walls in the direction it faces in order to prevent immediate collision
        min_distance_to_walls_x = self.grid.columns / 4
        min_distance_to_walls_y = self.grid.rows / 4

        if chosen_cell[0] > min_distance_to_walls_x:
            starting_orientations.append(Orientation.WEST)

        if self.grid.columns - chosen_cell[0] > min_distance_to_walls_x:
            starting_orientations.append(Orientation.EAST)

        if chosen_cell[1] > min_distance_to_walls_y:
            starting_orientations.append(Orientation.NORTH)

        if self.grid.rows - chosen_cell[1] > min_distance_to_walls_y:
            starting_orientations.append(Orientation.SOUTH)

        chosen_orientation = random.choice(starting_orientations)
        self.snake.set_orientation(chosen_orientation)

    def respawn_food(self):
        empty_cells = self.get_empty_cells()
        chosen_cell = random.choice(empty_cells)
        self.food.set_coordinates(chosen_cell)

    def snake_go_north(self):
        delta_coordinates = self.snake.head_coordinates - self.snake.head_coordinates_previous

        # Only allow going north when currently not going south
        if delta_coordinates[1] != 1:
            self.snake.set_orientation(Orientation.NORTH)

    def snake_go_east(self):
        delta_coordinates = self.snake.head_coordinates - self.snake.head_coordinates_previous

        # Only allow going east when currently not going west
        if delta_coordinates[0] != -1:
            self.snake.set_orientation(Orientation.EAST)

    def snake_go_south(self):
        delta_coordinates = self.snake.head_coordinates - self.snake.head_coordinates_previous

        # Only allow going south when currently not going north
        if delta_coordinates[1] != -1:
            self.snake.set_orientation(Orientation.SOUTH)

    def snake_go_west(self):
        delta_coordinates = self.snake.head_coordinates - self.snake.head_coordinates_previous

        # Only allow going west when currently not going east
        if delta_coordinates[0] != 1:
            self.snake.set_orientation(Orientation.WEST)

    def check_collision(self):
        snake = self.snake

        # Check if snake collides with own body
        for body_part_i_coordinates in snake.body_coordinates:
            if np.array_equal(snake.head_coordinates, body_part_i_coordinates):
                return True

        # Check if snake collides with walls
        if snake.head_coordinates[0] < 0 or snake.head_coordinates[0] > self.grid.columns - 1 or snake.head_coordinates[1] < 0 or snake.head_coordinates[1] > self.grid.rows - 1:
            return True

        return False

    def cell_is_empty(self, coordinates):
        snake = self.snake
        food = self.food

        if np.array_equal(coordinates, snake.head_coordinates):
            return False

        if np.array_equal(coordinates, food.coordinates):
            return False

        for body_part_coordinates in snake.body_coordinates:
            if np.array_equal(coordinates, body_part_coordinates):
                return False

        return True

    def get_empty_cells(self):
        empty_cells = []
        grid = self.grid

        for i in range(1, grid.rows - 1):
            for j in range(1, grid.columns - 1):
                cell_coordinates = np.array([j, i])

                if self.cell_is_empty(cell_coordinates):
                    empty_cells.append(cell_coordinates)

        return empty_cells

    def update(self):
        if self.snake.has_eaten_food:
            self.snake.grow()

        self.snake.update_position()

        if np.array_equal(self.snake.head_coordinates, self.food.coordinates):
            self.snake.eat_food()
            self.score += 1
            self.respawn_food()

        if self.check_collision():
            return False

        return True
