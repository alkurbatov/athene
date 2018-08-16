# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

"""Utility functions and classes to simplify work with the data received
   from feature_screen.
"""

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
