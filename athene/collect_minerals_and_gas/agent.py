# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

"""A simple agent to play in the CollectMineralsAndGas minigame.

To run this code do:
$ python -m pysc2.bin.agent --map CollectMineralsAndGas --agent athene.collect_minerals_and_gas.Agent
"""

import os

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import units

from athene.api.actions import \
    ACTION_BUILD_REFINERY, \
    ACTION_BUILD_SUPPLY, \
    ACTION_DO_NOTHING, \
    ACTION_HARVEST_MINERALS, \
    ACTION_SELECT_COMMAND_CENTER, \
    ACTION_SELECT_IDLE_WORKER, \
    ACTION_TRAIN_SCV
from athene.api.screen import UnitPos, UnitPosList
from athene.brain.qlearning import QLearningTable


class Agent(base_agent.BaseAgent):

    DATA_FOLDER = os.path.join('memory', 'collect_minerals_and_gas')

    def __init__(self):
        super().__init__()

        self.smart_actions = [
            ACTION_DO_NOTHING,
            ACTION_SELECT_IDLE_WORKER,
            ACTION_HARVEST_MINERALS,
            ACTION_SELECT_COMMAND_CENTER,
            ACTION_TRAIN_SCV,
            ACTION_BUILD_SUPPLY,
            ACTION_BUILD_REFINERY,
        ]

        self.qlearn = QLearningTable.load(
            actions=self.smart_actions,
            src=self.DATA_FOLDER,
        )

        self.town_hall = None
        self.previous_action = None
        self.previous_state = None

    def step(self, obs):
        super().step(obs)

        unit_type = obs.observation.feature_screen.unit_type

        if obs.first():
            cc_y, cc_x = (unit_type == units.Terran.CommandCenter).nonzero()
            self.town_hall = UnitPos(cc_x, cc_y)

        if obs.last():
            self.qlearn.learn(
                self.previous_state,
                self.previous_action,
                obs.reward,
                'terminal'
            )

            self.qlearn.dump(self.DATA_FOLDER)
            return actions.FUNCTIONS.no_op()

        supplies = UnitPosList.locate(obs, units.Terran.SupplyDepot)
        refineries = UnitPosList.locate(obs, units.Terran.Refinery)

        current_state = (
            obs.observation.player.idle_worker_count,
            obs.observation.player.food_workers,
            len(supplies),
            len(refineries)
        )

        excluded_actions = set()

        if obs.observation.player.idle_worker_count == 0:
            excluded_actions.add(ACTION_SELECT_IDLE_WORKER)
            excluded_actions.add(ACTION_HARVEST_MINERALS)

        if obs.observation.player.food_cap == obs.observation.player.food_used:
            excluded_actions.add(ACTION_SELECT_COMMAND_CENTER)
            excluded_actions.add(ACTION_TRAIN_SCV)

        if len(supplies) >= 2:
            excluded_actions.add(ACTION_BUILD_SUPPLY)

        if len(refineries) >= 4:
            excluded_actions.add(ACTION_BUILD_REFINERY)

        if self.previous_action:
            self.qlearn.learn(
                self.previous_state,
                self.previous_action,
                0,
                current_state
            )

        smart_action = self.qlearn.choose_action(
            current_state,
            excluded_actions=excluded_actions
        )

        self.previous_state = current_state
        self.previous_action = smart_action

        if smart_action == ACTION_SELECT_COMMAND_CENTER:
            cc_y, cc_x = (unit_type == units.Terran.CommandCenter).nonzero()

            if not cc_y.any():
                print('[WARNING] Where is your Command Center?')
                return actions.FUNCTIONS.no_op()

            # NOTE (alkurbatov): There is only one command center on the screen.
            cc = UnitPos(cc_x, cc_y)
            return actions.FUNCTIONS.select_point('select', cc.center)

        if smart_action == ACTION_TRAIN_SCV:
            if actions.FUNCTIONS.Train_SCV_quick.id not in obs.observation.available_actions:
                return actions.FUNCTIONS.no_op()

            return actions.FUNCTIONS.Train_SCV_quick('now')

        if smart_action == ACTION_SELECT_IDLE_WORKER:
            if actions.FUNCTIONS.select_idle_worker.id not in obs.observation.available_actions:
                return actions.FUNCTIONS.no_op()

            return actions.FUNCTIONS.select_idle_worker('select')

        if smart_action == ACTION_HARVEST_MINERALS:
            if actions.FUNCTIONS.Harvest_Gather_screen.id not in obs.observation.available_actions:
                return actions.FUNCTIONS.no_op()

            minerals = UnitPosList.locate(obs, units.Neutral.MineralField)

            if not minerals:
                print('[WARNING] No minerals?')
                return actions.FUNCTIONS.no_op()

            mineral_x, mineral_y = minerals.random_point()
            mineral_patch = UnitPos(mineral_x, mineral_y)

            return actions.FUNCTIONS.Harvest_Gather_screen('now', mineral_patch.pos)

        if smart_action == ACTION_BUILD_REFINERY:
            if actions.FUNCTIONS.Build_Refinery_screen.id not in obs.observation.available_actions:
                return actions.FUNCTIONS.no_op()

            geysers = UnitPosList.locate(obs, units.Neutral.VespeneGeyser)

            if not geysers:
                print('[WARNING] No geysers?')
                return actions.FUNCTIONS.no_op()

            geyser_x, geyser_y = geysers.random_point()
            geyser = UnitPos(geyser_x, geyser_y)

            return actions.FUNCTIONS.Build_Refinery_screen('now', geyser.pos)

        if smart_action == ACTION_BUILD_SUPPLY:
            if actions.FUNCTIONS.Build_SupplyDepot_screen.id not in obs.observation.available_actions:
                return actions.FUNCTIONS.no_op()

            if supplies:
                return actions.FUNCTIONS.Build_SupplyDepot_screen(
                    'now', self.town_hall.shift(0, -20).pos)

            return actions.FUNCTIONS.Build_SupplyDepot_screen(
                'now', self.town_hall.shift(0, 20).pos)

        return actions.FUNCTIONS.no_op()
