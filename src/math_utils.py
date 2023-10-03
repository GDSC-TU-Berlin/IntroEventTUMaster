from dataclasses import dataclass
import numpy as np
import pygame.math


Position = pygame.math.Vector2


@dataclass
class Angle:
    def __init__(self, rad):
        self.rad = rad

    def __add__(self, other):
        initial = Angle(self.rad)
        initial += other
        return initial

    def __sub__(self, other):
        initial = Angle(self.rad)
        initial -= other
        return initial

    def __iadd__(self, other):
        self.rad = (self.rad + other.rad) % (2 * np.pi)
        return self

    def __isub__(self, other):
        new_rad = self.rad - other.rad
        self.rad = 2 * np.pi + new_rad if new_rad < 0 else new_rad
        return self

    def __imul__(self, multiplier):
        self.rad = (self.rad * multiplier) % (2 * np.pi)
        return self

    def __mul__(self, multiplier):
        initial = Angle(self.rad)
        initial *= multiplier
        return initial

    def __idiv__(self, divisor):
        self.rad = (self.rad / divisor) % (2 * np.pi)
        return self

    def __truediv__(self, divisor):
        initial = Angle(self.rad)
        initial.rad /= divisor
        return initial

    def __gt__(self, other):
        return self.rad > other.rad

    def __eq__(self, other):
        return self.rad == other.rad

    def __lt__(self, other):
        return self.rad < other.rad

    def to_degrees(self) -> float:
        return np.rad2deg(self.rad)

    def is_in_bounds(self, lb, ub) -> bool:
        return ub > self or self > lb if lb > ub else ub > self > lb


@dataclass
class PolarCoordinate:
    def __init__(self, angle: Angle, radius: float):
        self.angle = angle
        self.radius = radius

    def to_cartesian(self) -> Position:
        return Position(
            self.radius * np.cos(self.angle.rad),
            -self.radius * np.sin(self.angle.rad)
        )
