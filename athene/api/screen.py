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
    Operates with approximate center of the provided geometry.
    """

    def __init__(self, pos_x, pos_y):
        if isinstance(pos_x, (list, tuple, numpy.ndarray)):
            center = numpy.mean(list(zip(pos_x, pos_y)), axis=0).round()
            self.pos_x = center[0]
            self.pos_y = center[1]
            return

        self.pos_x = pos_x
        self.pos_y = pos_y

    def __str__(self):
        return '(x:{}, y:{})'.format(self.pos_x, self.pos_y)

    @property
    def pos(self):
        """Get the unit's position on the map."""
        return [self.pos_x, self.pos_y]

    def shift(self, shift_x, shift_y):
        """Return shifted position of this unit."""
        return UnitPos(self.pos_x + shift_x, self.pos_y + shift_y)


class UnitPosList:
    """Generic representation of units list from feature_screen.unit_types.
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
        return UnitPos(self.pos_x[i], self.pos_y[i])

    def __len__(self):
        """Get units count."""
        return int(math.ceil(len(self.pos_y) / self.diameter))


class UnitPosClustersList(UnitPosList):
    """Another representation of units list from feature_screen.unit_types.
    The units positions are identified by forming clusters of points.

    WARNING: This method uses kmeans clustering which is precise but
    very very slow!
    """

    def __init__(self, pos_x, pos_y, diameter=None):
        super().__init__(pos_x, pos_y, diameter)

        kmeans = KMeans(n_clusters=len(self))
        kmeans.fit(list(zip(self.pos_x, self.pos_y)))

        self.cluster_centers = kmeans.cluster_centers_

    @staticmethod
    def locate(obs, unit_type):
        """Find all the visible units of the specified type and
        return as a list.
        """
        unit_types = obs.observation.feature_screen.unit_type
        units_y, units_x = (unit_types == unit_type).nonzero()
        return UnitPosClustersList(units_x, units_y,
                                   diameter=DIAMETERS.get(unit_type))

    def random_unit(self):
        """Select a random unit from the list.
        """
        random_unit = self.cluster_centers[random.randint(0, len(self) - 1)]
        return UnitPos(random_unit[0], random_unit[1])
