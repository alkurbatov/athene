# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

"""A simple agent to play in the CollectMineralsAndGas minigame.
According to the map rules spending of the minerals don't reduce the score.

To run this code do:
$ python -m pysc2.bin.agent --map CollectMineralsAndGas --agent athene.collect_minerals_and_gas.Agent
"""

import os

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import units

from athene.api.actions import \
    ACTION_BUILD_COMMAND_CENTER, \
    ACTION_BUILD_REFINERY, \
    ACTION_BUILD_SUPPLY, \
    ACTION_DO_NOTHING, \
    ACTION_HARVEST_MINERALS, \
    ACTION_TRAIN_SCV
from athene.api.actions import Stages, cannot, cannot_afford
from athene.api.screen import UnitPos, UnitPosList, UnitPosClustersList
from athene.brain.qlearning import QLearningTable
from athene.metrics import store


class Agent(base_agent.BaseAgent):

    DATA_FOLDER = os.path.join('memory', 'collect_minerals_and_gas')

    SMART_ACTIONS = [
        ACTION_DO_NOTHING,
        ACTION_BUILD_COMMAND_CENTER,
        ACTION_HARVEST_MINERALS,
        ACTION_TRAIN_SCV,
        ACTION_BUILD_SUPPLY,
        ACTION_BUILD_REFINERY,
    ]

    def __init__(self):
        super().__init__()

        self.qlearn = QLearningTable.load(
            actions=self.SMART_ACTIONS,
            src=self.DATA_FOLDER,
        )

        self.stage = None

        self.minerals = None
        self.geysers = None

        self.town_hall = None
        self.executed_action = None
        self.previous_state = None

        self.metrics = store.Score(self.DATA_FOLDER)

    def step(self, obs):
        super().step(obs)

        unit_type = obs.observation.feature_screen.unit_type

        if obs.first():
            self.stage = Stages.CHOOSE_ACTION
            cc_y, cc_x = (unit_type == units.Terran.CommandCenter).nonzero()
            self.town_hall = UnitPos(cc_x, cc_y)

            # NOTE (alkurbatov): Cache positions of mineral patches and geysers.
            self.minerals = UnitPosClustersList.locate(
                obs,
                units.Neutral.MineralField)
            self.geysers = UnitPosClustersList.locate(
                obs,
                units.Neutral.VespeneGeyser)

        if obs.last():
            self.qlearn.learn(
                self.previous_state,
                self.executed_action,
                obs.reward,
                'terminal'
            )

            self.qlearn.dump(self.DATA_FOLDER)
            self.metrics.record(obs.observation.score_cumulative.score)
            return actions.FUNCTIONS.no_op()

        supplies = UnitPosList.locate(obs, units.Terran.SupplyDepot)

        if self.stage == Stages.CHOOSE_ACTION:
            self.stage = Stages.SELECT_UNIT

            town_halls = UnitPosList.locate(obs, units.Terran.CommandCenter)
            refineries = UnitPosList.locate(obs, units.Terran.Refinery)

            current_state = (
                obs.observation.player.idle_worker_count,
                obs.observation.player.food_workers,
                len(town_halls),
                len(supplies),
                len(refineries)
            )

            if self.executed_action:
                self.qlearn.learn(
                    self.previous_state,
                    self.executed_action,
                    0,
                    current_state
                )

            excluded_actions = set()

            if obs.observation.player.idle_worker_count == 0:
                excluded_actions.add(ACTION_HARVEST_MINERALS)

            if obs.observation.player.food_cap == obs.observation.player.food_used or \
                    cannot_afford(obs, ACTION_TRAIN_SCV):
                excluded_actions.add(ACTION_TRAIN_SCV)

            if len(supplies) >= 2 or cannot_afford(obs, ACTION_BUILD_SUPPLY):
                excluded_actions.add(ACTION_BUILD_SUPPLY)

            if not self.geysers or cannot_afford(obs, ACTION_BUILD_REFINERY):
                excluded_actions.add(ACTION_BUILD_REFINERY)

            if len(town_halls) >= 2 or cannot_afford(obs, ACTION_BUILD_COMMAND_CENTER):
                excluded_actions.add(ACTION_BUILD_COMMAND_CENTER)

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

            return actions.FUNCTIONS.no_op()

        if self.executed_action == ACTION_DO_NOTHING:
            self.stage = Stages.CHOOSE_ACTION
            return actions.FUNCTIONS.no_op()

        if self.stage == Stages.SELECT_UNIT:
            self.stage = Stages.ISSUE_ORDER

            if self.executed_action == ACTION_TRAIN_SCV:
                cc_y, cc_x = (unit_type == units.Terran.CommandCenter).nonzero()

                cc = UnitPosList.locate(obs, units.Terran.CommandCenter).random_point()
                return actions.FUNCTIONS.select_point('select', cc.pos)

            if self.executed_action == ACTION_HARVEST_MINERALS:
                if cannot(obs, actions.FUNCTIONS.select_idle_worker.id):
                    return actions.FUNCTIONS.no_op()

                return actions.FUNCTIONS.select_idle_worker('select')

            # NOTE (alkurbatov): All other actions require an SCV.
            scv = UnitPosList.locate(obs, units.Terran.SCV).random_point()
            return actions.FUNCTIONS.select_point('select', scv.pos)

        if self.stage == Stages.ISSUE_ORDER:
            self.stage = Stages.CHOOSE_ACTION

            if self.executed_action == ACTION_TRAIN_SCV:
                if cannot(obs, actions.FUNCTIONS.Train_SCV_quick.id):
                    return actions.FUNCTIONS.no_op()

                return actions.FUNCTIONS.Train_SCV_quick('now')

            if self.executed_action == ACTION_HARVEST_MINERALS:
                mineral_patch = self.minerals.random_unit()
                return actions.FUNCTIONS.Harvest_Gather_screen('now', mineral_patch.pos)

            if self.executed_action == ACTION_BUILD_REFINERY:
                if cannot(obs, actions.FUNCTIONS.Build_Refinery_screen.id):
                    return actions.FUNCTIONS.no_op()

                geyser = self.geysers.pop_random_unit()
                return actions.FUNCTIONS.Build_Refinery_screen('now', geyser.pos)

            if self.executed_action == ACTION_BUILD_SUPPLY:
                if cannot(obs, actions.FUNCTIONS.Build_SupplyDepot_screen.id):
                    return actions.FUNCTIONS.no_op()

                if supplies:
                    return actions.FUNCTIONS.Build_SupplyDepot_screen(
                        'now', self.town_hall.shift(0, -20).pos)

                return actions.FUNCTIONS.Build_SupplyDepot_screen(
                    'now', self.town_hall.shift(0, 20).pos)

            if self.executed_action == ACTION_BUILD_COMMAND_CENTER:
                if cannot(obs, actions.FUNCTIONS.Build_CommandCenter_screen.id):
                    return actions.FUNCTIONS.no_op()

                return actions.FUNCTIONS.Build_CommandCenter_screen(
                    'now', self.town_hall.shift(16, 0).pos)

        return actions.FUNCTIONS.no_op()
