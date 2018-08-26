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
    ACTION_TRAIN_SCV
from athene.api.actions import cannot
from athene.api.screen import UnitPos, UnitPosList
from athene.brain.qlearning import QLearningTable


class Agent(base_agent.BaseAgent):

    DATA_FOLDER = os.path.join('memory', 'collect_minerals_and_gas')

    def __init__(self):
        super().__init__()

        self.smart_actions = [
            ACTION_DO_NOTHING,
            ACTION_HARVEST_MINERALS,
            ACTION_TRAIN_SCV,
            ACTION_BUILD_SUPPLY,
            ACTION_BUILD_REFINERY,
        ]

        self.qlearn = QLearningTable.load(
            actions=self.smart_actions,
            src=self.DATA_FOLDER,
        )

        # NOTE (alkurbatov): Many tasks are done in to steps (stages):
        # 1 - Select a unit.
        # 2 - Issue an order.
        self.stage = 0

        self.town_hall = None
        self.executed_action = None
        self.previous_state = None

    def step(self, obs):
        super().step(obs)

        unit_type = obs.observation.feature_screen.unit_type

        if obs.first():
            self.stage = 1
            cc_y, cc_x = (unit_type == units.Terran.CommandCenter).nonzero()
            self.town_hall = UnitPos(cc_x, cc_y)

        if obs.last():
            self.qlearn.learn(
                self.previous_state,
                self.executed_action,
                obs.reward,
                'terminal'
            )

            self.qlearn.dump(self.DATA_FOLDER)
            return actions.FUNCTIONS.no_op()

        supplies = UnitPosList.locate(obs, units.Terran.SupplyDepot)

        if self.stage == 1:
            self.stage += 1

            refineries = UnitPosList.locate(obs, units.Terran.Refinery)

            current_state = (
                obs.observation.player.idle_worker_count,
                obs.observation.player.food_workers,
                len(supplies),
                len(refineries)
            )

            excluded_actions = set()

            if obs.observation.player.idle_worker_count == 0:
                excluded_actions.add(ACTION_HARVEST_MINERALS)

            if obs.observation.player.food_cap == obs.observation.player.food_used:
                excluded_actions.add(ACTION_TRAIN_SCV)

            if len(supplies) >= 2:
                excluded_actions.add(ACTION_BUILD_SUPPLY)

            if len(refineries) >= 4:
                excluded_actions.add(ACTION_BUILD_REFINERY)

            if self.executed_action:
                self.qlearn.learn(
                    self.previous_state,
                    self.executed_action,
                    0,
                    current_state
                )

            smart_action = self.qlearn.choose_action(
                current_state,
                excluded_actions=excluded_actions
            )

            self.previous_state = current_state
            self.executed_action = smart_action

            if smart_action == ACTION_DO_NOTHING:
                return actions.FUNCTIONS.no_op()

            if smart_action == ACTION_TRAIN_SCV:
                cc_y, cc_x = (unit_type == units.Terran.CommandCenter).nonzero()

                # NOTE (alkurbatov): There is only one command center on the screen.
                cc = UnitPos(cc_x, cc_y)
                return actions.FUNCTIONS.select_point('select', cc.center)

            if smart_action == ACTION_HARVEST_MINERALS:
                if cannot(obs, actions.FUNCTIONS.select_idle_worker.id):
                    return actions.FUNCTIONS.no_op()

                return actions.FUNCTIONS.select_idle_worker('select')

            # NOTE (alkurbatov): All other actions require an SCV.
            scv = UnitPosList.locate(obs, units.Terran.SCV).random_point()
            return actions.FUNCTIONS.select_point('select', scv.pos)

        if self.stage == 2:
            self.stage = 1

            if self.executed_action == ACTION_TRAIN_SCV:
                if cannot(obs, actions.FUNCTIONS.Train_SCV_quick.id):
                    return actions.FUNCTIONS.no_op()

                return actions.FUNCTIONS.Train_SCV_quick('now')

            if self.executed_action == ACTION_HARVEST_MINERALS:
                minerals = UnitPosList.locate(obs, units.Neutral.MineralField)
                mineral_patch = minerals.random_unit()

                return actions.FUNCTIONS.Harvest_Gather_screen('now', mineral_patch.pos)

            if self.executed_action == ACTION_BUILD_REFINERY:
                if cannot(obs, actions.FUNCTIONS.Build_Refinery_screen.id):
                    return actions.FUNCTIONS.no_op()

                geysers = UnitPosList.locate(obs, units.Neutral.VespeneGeyser)
                geyser = geysers.random_unit()

                return actions.FUNCTIONS.Build_Refinery_screen('now', geyser.pos)

            if self.executed_action == ACTION_BUILD_SUPPLY:
                if cannot(obs, actions.FUNCTIONS.Build_SupplyDepot_screen.id):
                    return actions.FUNCTIONS.no_op()

                if supplies:
                    return actions.FUNCTIONS.Build_SupplyDepot_screen(
                        'now', self.town_hall.shift(0, -20).pos)

                return actions.FUNCTIONS.Build_SupplyDepot_screen(
                    'now', self.town_hall.shift(0, 20).pos)

        return actions.FUNCTIONS.no_op()
