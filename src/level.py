import random
from dataclasses import dataclass
from typing import List
from math_utils import Position
from random import shuffle
from player import Player


@dataclass
class Obstacle:
    DEFAULT_RADIUS = 5
    DEFAULT_COLOR = 'green'
    DEFAULT_COLOR_IN_SIGHT = 'red'

    def __init__(self, position: Position, color=DEFAULT_COLOR):
        self.position = position
        self.color = color


@dataclass
class Cell:
    def __init__(self, wall_up=True, wall_left=True):
        self.wall_up = wall_up
        self.wall_left = wall_left
        self.is_visited = False


class Level:
    DEFAULT_MAZE_DIMENSIONS = (4, 4)
    TARGET_COLOR = 'gold'
    TARGET_RADIUS = 30

    def __init__(self, width=DEFAULT_MAZE_DIMENSIONS[0], height=DEFAULT_MAZE_DIMENSIONS[1]):
        self.width = width
        self.height = height
        self.grid: List[List[Cell]] = []
        self.obstacles: List[Obstacle] = []
        self.start_position = None
        self.target = None

        for i in range(width):
            self.grid.append([])
            for j in range(height):
                self.grid[i].append(Cell())

        self.generate_maze()

    def generate_objects(self, screen_width, screen_height, obstacle_radius):
        cell_width = screen_width / self.width
        cell_height = screen_height / self.height
        Player.VIEWING_BOUNDS.radius *= min(cell_width, cell_height)

        obstacles_per_horizontal_wall = int(cell_width / obstacle_radius)
        obstacles_per_vertical_wall = int(cell_height / obstacle_radius)

        self.start_position = (
            cell_width * (self.start_position[0] + 0.5),
            cell_height * (self.start_position[1] + 0.5)
        )

        self.target = Position(
            cell_width * (self.target[0] + 0.5),
            cell_height * (self.target[1] + 0.5)
        )

        self.generate_border_obstacles(
            screen_width, screen_height, obstacle_radius
        )

        for i in range(self.width):
            for j in range(self.height):
                cell = self.grid[i][j]
                x = cell_width * (i + 0.5)
                y = cell_height * (j + 0.5)
                if cell.wall_up:
                    self.generate_wall_above(
                        x, y,
                        cell_width, cell_height,
                        obstacles_per_horizontal_wall
                    )
                if cell.wall_left:
                    self.generate_wall_left_of(
                        x, y,
                        cell_width, cell_height,
                        obstacles_per_vertical_wall
                    )

    def generate_wall_above(
        self,
        x, y,
        cell_width, cell_height,
        obstacles_per_horizontal_wall
    ):
        step_size = cell_width / obstacles_per_horizontal_wall
        wall_y = y - cell_height / 2
        wall_x_start = x - cell_width / 2

        for i in range(obstacles_per_horizontal_wall):
            current_x = wall_x_start + i * step_size
            self.obstacles.append(Obstacle(Position(current_x, wall_y)))

    def generate_wall_left_of(
        self,
        x, y,
        cell_width, cell_height,
        obstacles_per_vertical_wall
    ):
        step_size = cell_height / obstacles_per_vertical_wall
        wall_x = x - cell_width / 2
        wall_y_start = y - cell_height / 2

        for i in range(obstacles_per_vertical_wall):
            current_y = wall_y_start + i * step_size
            self.obstacles.append(Obstacle(Position(wall_x, current_y)))

    def generate_border_obstacles(
        self,
        screen_width, screen_height,
        obstacle_radius
    ):
        num_x_steps = int(screen_width / obstacle_radius)
        num_y_steps = int(screen_height / obstacle_radius)

        for i in range(num_x_steps):
            current_x = i * obstacle_radius
            self.obstacles.append(Obstacle(Position(current_x, screen_height)))

        for i in range(num_y_steps):
            current_y = i * obstacle_radius
            self.obstacles.append(Obstacle(Position(screen_width, current_y)))

    def generate_maze(self):
        x_start = random.randrange(0, self.width)
        y_start = random.randrange(0, self.height)
        self.start_position = (x_start, y_start)

        x_target = random.randrange(0, self.width)
        y_target = random.randrange(0, self.height)
        while x_target == x_start and y_target == y_start:
            x_target = random.randrange(0, self.width)
            y_target = random.randrange(0, self.height)

        self.target = (x_target, y_target)

        self.recursive_dfs(x_start, y_start)

    def recursive_dfs(self, x, y):
        cell = self.grid[x][y]
        cell.is_visited = True

        order = list(range(4))
        shuffle(order)

        for i in order:
            if i == 0:
                self.try_cell_above(x, y, cell)
            elif i == 1:
                self.try_cell_below(x, y)
            elif i == 2:
                self.try_cell_left_of(x, y, cell)
            else:
                self.try_cell_right_of(x, y)

    def try_cell_above(self, x, y, previous_cell):
        up_coords = self.get_cell_above(x, y)
        if up_coords[0] >= 0:
            cell_above = self.grid[up_coords[0]][up_coords[1]]
            if not cell_above.is_visited:
                previous_cell.wall_up = False
                self.recursive_dfs(*up_coords)

    def try_cell_below(self, x, y):
        down_coords = self.get_cell_below(x, y)
        if down_coords[0] >= 0:
            cell_below = self.grid[down_coords[0]][down_coords[1]]
            if not cell_below.is_visited:
                cell_below.wall_up = False
                self.recursive_dfs(*down_coords)

    def try_cell_left_of(self, x, y, previous_cell):
        left_coords = self.get_cell_left_of(x, y)
        if left_coords[0] >= 0:
            left_cell = self.grid[left_coords[0]][left_coords[1]]
            if not left_cell.is_visited:
                previous_cell.wall_left = False
                self.recursive_dfs(*left_coords)

    def try_cell_right_of(self, x, y):
        right_coords = self.get_cell_right_of(x, y)
        if right_coords[0] >= 0:
            right_cell = self.grid[right_coords[0]][right_coords[1]]
            if not right_cell.is_visited:
                right_cell.wall_left = False
                self.recursive_dfs(*right_coords)

    @staticmethod
    def get_cell_above(x, y) -> (int, int):
        return (-1, -1) if y == 0 else (x, y - 1)

    def get_cell_below(self, x, y) -> (int, int):
        return (-1, -1) if y == self.height - 1 else (x, y + 1)

    @staticmethod
    def get_cell_left_of(x, y) -> (int, int):
        return (-1, -1) if x == 0 else (x - 1, y)

    def get_cell_right_of(self, x, y) -> (int, int):
        return (-1, -1) if x == self.width - 1 else (x + 1, y)
