# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

"""Utility functions and classes to simplify work with the data received
   from feature_screen.
"""

import random

import numpy


class UnitPos:
    """Generic representation of a unit received from feature_screen.unit_types.
    """

    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y

    @property
    def center(self):
        """Get coordinates of the unit's center."""
        return numpy.mean(list(zip(self.pos_x, self.pos_y)), axis=0).round()

    @property
    def pos(self):
        """Get the unit's position on the map."""
        return [self.pos_x, self.pos_y]

    def shift(self, shift_x, shift_y):
        """Return shifted position of this unit."""
        center = self.center
        return UnitPos(center[0] + shift_x, center[1] + shift_y)


class UnitPosList:
    """Generic representation of of units list from feature_screen.unit_types.
    """

    def __init__(self, pos_x, pos_y, diameter=None):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.diameter = diameter

    def any(self):
        """Returns true if there is at list one item in the list."""
        return self.pos_y.any()

    def random_point(self):
        """Select a random point from the list."""
        i = random.randint(0, len(self.pos_y) - 1)
        return self.pos_x[i], self.pos_y[i]

    @property
    def count(self):
        """Get units count."""
        return int(round(len(self.pos_y) / self.diameter))
