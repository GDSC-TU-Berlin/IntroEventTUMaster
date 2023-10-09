import enum
from math_utils import *


class Direction(enum.Enum):
    Left = 1
    Center = 2
    Right = 3


class Player:
    MOVEMENT_SPEED = 3
    TURNING_SPEED = Angle(1 / (32 * np.pi))
    """radius becomes radius * min(cell width, cell height) of maze, see Level.generate_obstacles"""
    VIEWING_BOUNDS = PolarCoordinate(Angle(np.pi / 5), 1.5)
    COLOR = 'blue'
    BODY_RADIUS = 20
    FRUSTUM_COLOR = 'white'
    DIRECTION_TO_PANNING = {
        Direction.Left: 0.1,
        Direction.Center: 0.5,
        Direction.Right: 0.9
    }

    def __init__(
        self,
        position: Position,
        direction: Angle,
        screen_dimensions: (int, int)
    ):
        self.position = position
        self.direction = direction
        self.screen_dimensions = screen_dimensions

    def turn_right(self):
        self.direction -= Player.TURNING_SPEED

    def turn_left(self):
        self.direction += Player.TURNING_SPEED

    def move_forward(self):
        increment = PolarCoordinate(self.direction, Player.MOVEMENT_SPEED).to_cartesian()
        next_position = self.position + increment
        if self.is_in_screen_bounds(next_position):
            self.position = next_position

    def is_in_screen_bounds(self, position: Position) -> bool:
        return (
            0 < position.y < self.screen_dimensions[1]
            and 0 < position.x < self.screen_dimensions[0]
        )

    def is_facing(self, point: PolarCoordinate) -> bool:
        upper_bound = self.direction + Player.VIEWING_BOUNDS.angle
        lower_bound = self.direction - Player.VIEWING_BOUNDS.angle

        return point.angle.is_in_bounds(lower_bound, upper_bound)

    def can_see(self, point: PolarCoordinate) -> bool:
        is_close_enough = point.radius <= Player.VIEWING_BOUNDS.radius

        return is_close_enough and self.is_facing(point)

    def world_position_to_relative_polar_coordinate(self, other: Position) -> PolarCoordinate:
        """
        Convert a position in world coordinates (screen coordinates) to
        a polar coordinate relative to the player

        :param other: position to convert
        :return: converted polar coordinate
        """
        vec = other - self.position

        """flip y-coordinate system because pixel coordinate system is upside down"""
        rad = np.arctan2(-vec.y, vec.x)

        """shift range from [-PI, PI] to [0, 2PI]"""
        if rad < 0:
            rad += 2 * np.pi

        return PolarCoordinate(Angle(rad), vec.length())

    def relative_polar_coordinate_to_world_position(self, other: PolarCoordinate) -> Position:
        """
        Convert a polar coordinate relative to the player to a position
        in world coordinates

        :param other: polar coordinate to convert
        :return: corresponding position
        """
        return self.position + other.to_cartesian()

    def direction_relative_to_player(self, point: PolarCoordinate) -> Direction:
        """
        Given a point is within the viewing bounds of the player,
        find out if it is positioned to the left, to the right, or
        in the center

        :param point: a polar coordinate within the viewing bounds
        :return: Left, Center or Right
        """
        section_arc_length = Player.VIEWING_BOUNDS.angle * (2 / 3)

        left_bound = self.direction + Player.VIEWING_BOUNDS.angle
        right_bound = self.direction - Player.VIEWING_BOUNDS.angle
        left_center_bound = left_bound - section_arc_length
        right_center_bound = right_bound + section_arc_length

        if point.angle.is_in_bounds(left_center_bound, left_bound):
            return Direction.Left
        if point.angle.is_in_bounds(right_center_bound, left_center_bound):
            return Direction.Center
        else:
            return Direction.Right

    def distance_to(self, other: Position) -> float:
        return (self.position - other).length()
