# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

"""A set of various handy geometry constants.
All values measured in number of points.
"""

from pysc2.lib import units


DIAMETERS = {
    units.Neutral.MineralField: 42,
    units.Neutral.VespeneGeyser: 97,
    units.Terran.Marine: 9,
    units.Terran.Refinery: 112,
    units.Terran.SCV: 12,
    units.Terran.SupplyDepot: 69,
}
