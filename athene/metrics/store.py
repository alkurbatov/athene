# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Alexander Kurbatov

import os


class Score:
    """Store the score across episodes in .CSV format."""

    def __init__(self, dst):
        self.dst = os.path.join(dst, 'score.csv')

        with open(self.dst, 'a') as f:
            f.write('score\n')

    def record(self, score):
        """Add record to the file."""
        with open(self.dst, 'a') as f:
            f.write(str(score) + '\n')
