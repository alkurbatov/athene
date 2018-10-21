# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

"""A set of actions definitions."""

import enum

# General
ACTION_ATTACK = 'attack'
ACTION_DO_NOTHING = 'donothing'
ACTION_HARVEST_MINERALS = 'harvestminerals'
ACTION_MOVE_TO_BEACON = 'movetobeacon'
ACTION_SELECT_IDLE_WORKER = 'select_idle_worker'

# Terran
ACTION_BUILD_COMMAND_CENTER = 'buildcc'
ACTION_BUILD_REFINERY = 'buildrefinery'
ACTION_BUILD_SUPPLY = 'buildsupply'
ACTION_SELECT_MARINE = 'selectmarine'
ACTION_SELECT_COMMAND_CENTER = 'selectcc'
ACTION_SELECT_SCV = 'selectscv'
ACTION_TRAIN_SCV = 'trainscv'

# Zerg
ACTION_BUILD_SPAWNING_POOL = 'buildspawningpool'
ACTION_SPAWN_DRONE = 'spawndrone'
ACTION_SPAWN_OVERLORD = 'spawnoverlord'
ACTION_SPAWN_ZERGLINGS = 'spawnzerglings'


COSTS = {
    ACTION_BUILD_COMMAND_CENTER: 400,
    ACTION_BUILD_REFINERY: 75,
    ACTION_TRAIN_SCV: 50,
    ACTION_BUILD_SUPPLY: 100,
}


@enum.unique
class Stages(enum.IntEnum):
    """Many tasks are done in two or more steps (stages), e.g.
    #1 - Select unit.
    #2 - Issue order.

    This enumeration contains predefined values for the stages.
    """

    CHOOSE_ACTION = 0
    SELECT_UNIT = 1
    ISSUE_ORDER = 2


def can(obs, action_id):
    """Returns True if the specified action is available."""
    return action_id in obs.observation.available_actions


def cannot(obs, action_id):
    """Returns True if the specified action is not available."""
    return not can(obs, action_id)


def cannot_afford(obs, action_id):
    """Returns True if there is not enough resources for the specified
    action (e.g. to create a building or train a unit).
    """
    return obs.observation.player.minerals <= COSTS.get(action_id, 0)
