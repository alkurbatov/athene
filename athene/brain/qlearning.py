# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

"""My implementation of the QLearning table."""

import os
import shutil

import numpy
import pandas


class QLearningTable:
    """Implementation of QLearning table. Based on
        https://github.com/MorvanZhou/Reinforcement-learning-with-tensorflow

        Meaning of variables:
        alpha   - the learning rate.
        gamma   - the reward decay aka discounting rate. The larger the gamma,
                  the smaller the discount, which means that the agent cares
                  more about the long term reward.
        epsilon - the exploration rate aka the greedy policy factor.
                  The exploration means finding more about the environment.
    """

    def __init__(self, actions, alpha=0.01, gamma=0.9, epsilon=0.9):
        self.disallowed_actions = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = pandas.DataFrame(columns=actions, dtype=numpy.float64)

    def choose_action(self, current_state, excluded_actions=None):
        """Choose the next action based on the current state."""
        current_state = str(current_state)
        self._register_state(current_state)

        state_actions = self.q_table.loc[current_state, :]

        if excluded_actions:
            self.disallowed_actions[current_state] = excluded_actions

            # NOTE (alkurbatov): Filter excluded actions from
            # the possible choices, so the agent will not take
            # an invalid action.
            items = set(self.q_table.columns) - excluded_actions
            state_actions = state_actions.filter(items=items)

        if numpy.random.uniform() < self.epsilon:
            # NOTE (alkurbatov): Try to choose the best action
            # available in the current state.
            # Some actions could have equal weights, select random one
            # in this case.
            state_actions = state_actions.reindex(
                numpy.random.permutation(state_actions.index))
            action = state_actions.idxmax()
        else:
            # NOTE (alkurbatov): Time for exploration.
            action = numpy.random.choice(state_actions.index)

        return action

    def learn(self, s, a, r, s_):
        """Learn using the Qlearning algorithm.

            Meaning of variables:
            s - a previous state.
            a - a previous action.
            r - a reward received after the execution of the previous action.
            s_ - a next state.
        """
        s = str(s)
        s_ = str(s_)

        if s == s_:
            # NOTE (alkurbatov): No changes in the state, nothing to learn.
            return

        self._register_state(s_)

        q_predict = self.q_table.loc[s, a]

        if s_ == 'terminal':
            # NOTE (alkurbatov): The current state is terminal
            # which means end of the episode. The reward applied at this step
            # is sparse reward.
            q_target = r
        else:
            rewards = self.q_table.loc[s_, :]

            if s_ in self.disallowed_actions:
                # NOTE (alkurbatov): Since the invalid actions never get
                # chosen, their rewards never change. If they start at 0
                # then they could become the highest value action
                # for that state if all other actions have negative values.
                # To get around this, we filter the invalid actions from
                # the next state’s rewards.
                items = set(self.q_table.columns) - self.disallowed_actions[s_]
                rewards = rewards.filter(items=items)

            q_target = r + self.gamma * rewards.max()

        self.q_table.loc[s, a] += self.alpha * (q_target - q_predict)

    @staticmethod
    def load(actions, src, reset=False):
        """Initialize Qtable from the specified folder."""
        q_learn = QLearningTable(actions)

        if os.path.isdir(src) and reset:
            shutil.rmtree(src)

        os.makedirs(src, exist_ok=True)

        data_dump = os.path.join(src, 'qlearn.gz')
        if os.path.isfile(data_dump):
            q_learn.q_table = pandas.read_pickle(data_dump, compression='gzip')

        return q_learn

    def dump(self, dst):
        """Dump Qtable to the specified folder."""
        self.q_table.to_pickle(os.path.join(dst, 'qlearn.gz'), 'gzip')
        self.q_table.to_csv(os.path.join(dst, 'qlearn.csv'))

    def _register_state(self, current_state):
        """If the current state doesn't exist in QTable, add it."""
        if current_state in self.q_table.index:
            return

        self.q_table = self.q_table.append(
            pandas.Series(
                [0] * len(self.q_table.columns),
                index=self.q_table.columns,
                name=current_state
            )
        )
