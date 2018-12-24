# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

"""A simple agent to play in the MoveToBeacon minigame.
There is not much of machine learning inside because the purpose is
to set up a very simple agent and test that everything works on a very simple
task.

Here we use a very simple state machine to complete the task in two iterations.

To run this code do:
$ python -m pysc2.bin.agent --map MoveToBeacon --agent athene.minigames.move_to_beacon.Agent
"""

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features
from pysc2.lib import units

from athene.api.actions import \
    ACTION_DO_NOTHING, \
    ACTION_MOVE_TO_BEACON, \
    ACTION_SELECT_MARINE
from athene.api.geometry import DIAMETERS
from athene.api.screen import UnitPos


class Agent(base_agent.BaseAgent):

    def __init__(self):
        super().__init__()

        self.smart_action = ACTION_DO_NOTHING

    def step(self, obs):
        super().step(obs)

        if obs.first():
            print('[INFO] Game started!')
            self.smart_action = ACTION_SELECT_MARINE
            return actions.FUNCTIONS.no_op()

        if obs.last():
            print('[INFO] Game Finished!')
            return actions.FUNCTIONS.no_op()

        if self.smart_action == ACTION_SELECT_MARINE:
            unit_type = obs.observation.feature_screen.unit_type
            marine_y, marine_x = (unit_type == units.Terran.Marine).nonzero()

            if not marine_y.any():
                # NOTE (alkurbatov): Sometimes we are too fast and the marine
                # hasn't been placed on the screen yet.
                return actions.FUNCTIONS.no_op()

            if len(marine_y) < DIAMETERS.get(units.Terran.Marine):
                # NOTE (alkurbatov): Sometimes we receive not fully formed
                # marine coordinates probably because we are too fast again.
                # Just ignore it.
                return actions.FUNCTIONS.no_op()

            # NOTE (alkurbatov): There is only one marine on the screen and
            # no other objects around it so it is safe to select any point
            # in the list.
            marine = UnitPos(marine_x, marine_y)

            self.smart_action = ACTION_MOVE_TO_BEACON
            return actions.FUNCTIONS.select_point('select', marine.pos)

        if self.smart_action == ACTION_MOVE_TO_BEACON:
            if actions.FUNCTIONS.Move_screen.id not in obs.observation.available_actions:
                print('[WARNING] Nothing selected?')
                self.smart_action = ACTION_SELECT_MARINE
                return actions.FUNCTIONS.no_op()

            player_relative = obs.observation.feature_screen.player_relative
            beacon_y, beacon_x = (player_relative == features.PlayerRelative.NEUTRAL).nonzero()
            if not beacon_y.any():
                print('[WARNING] Where is your beacon?')
                return actions.FUNCTIONS.no_op()

            beacon = UnitPos(beacon_x, beacon_y)

            return actions.FUNCTIONS.Move_screen('now', beacon.pos)

        return actions.FUNCTIONS.no_op()
