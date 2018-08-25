# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

"""Utility functions and classes to simplify work with the data received
   from feature_screen.
"""

import math
import random

import numpy
from sklearn.cluster import KMeans

from .geometry import DIAMETERS


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

    @staticmethod
    def locate(obs, unit_type):
        """Find all the visible units of the specified type and
        return as a list.
        """
        unit_types = obs.observation.feature_screen.unit_type
        units_y, units_x = (unit_types == unit_type).nonzero()
        return UnitPosList(units_x, units_y, diameter=DIAMETERS.get(unit_type))

    def __nonzero__(self):
        """Returns false if there are no items in the list."""
        return self.pos_y.any()

    def random_point(self):
        """Select a random point from the list."""
        i = random.randint(0, len(self.pos_y) - 1)
        return self.pos_x[i], self.pos_y[i]

    def random_unit(self):
        """Select a random unit from the list.
        WARNING: This method uses kmeans clustering which is precise but
        very very slow!
        """
        kmeans = KMeans(n_clusters=len(self))
        kmeans.fit(list(zip(self.pos_x, self.pos_y)))

        random_unit = kmeans.cluster_centers_[random.randint(0, len(self) - 1)]
        return UnitPos(random_unit[0], random_unit[1])

    def __len__(self):
        """Get units count."""
        return int(math.ceil(len(self.pos_y) / self.diameter))
