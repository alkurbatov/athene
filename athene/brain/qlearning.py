# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

"""My implementation of the QLearning table."""

import os

import numpy
import pandas


class QLearningTable:
    """Implementation of QLearning table. Based on
        https://github.com/MorvanZhou/Reinforcement-learning-with-tensorflow

        Meaning of variables:
        alpha - the learning rate.
        gamma - the reward decay aka discount factor.
        epsilon - the exploration rate aka the greedy policy factor.
    """

    def __init__(self, actions, alpha=0.01, gamma=0.9, epsilon=0.9):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = pandas.DataFrame(
            columns=self.actions, dtype=numpy.float64)

    def choose_action(self, current_state):
        """Choose the next action based on the current state."""
        current_state = str(current_state)

        self._register_state(current_state)

        if numpy.random.uniform() < self.epsilon:
            # NOTE (alkurbatov): Try to choose the best action
            # available in the current state.
            state_action = self.q_table.loc[current_state, :]

            # NOTE (alkurbatov): Some actions could have equal weights.
            # Select random one in this case.
            state_action = state_action.reindex(numpy.random.permutation(state_action.index))
            action = state_action.idxmax()
        else:
            # NOTE (alkurbatov): Time for exploration.
            action = numpy.random.choice(self.actions)

        return action

    def learn(self, s, a, r, s_):
        """Learn using the Qlearning algorithm,

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
            q_target = r + self.gamma * self.q_table.loc[s_, :].max()

        self.q_table.loc[s, a] += self.alpha * (q_target - q_predict)

    @staticmethod
    def load(actions, src):
        """Initialize Qtable from the specified folder."""
        q_learn = QLearningTable(actions)

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
                [0] * len(self.actions),
                index=self.q_table.columns,
                name=current_state
            )
        )
