# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

"""A set of various handy geometry constants.
All values measured in number of points assuming that the screens resolution is
84x84 pixels (defaults).
For more info please check
https://itnext.io/how-to-locate-and-select-units-in-pysc2-2bb1c81f2ad3
"""

from pysc2.lib import units


DIAMETERS = {
    units.Neutral.MineralField: 44,
    units.Neutral.VespeneGeyser: 97,
    units.Terran.CommandCenter: 287,
    units.Terran.Marine: 9,
    units.Terran.Refinery: 112,
    units.Terran.SCV: 12,
    units.Terran.SupplyDepot: 69,
}
