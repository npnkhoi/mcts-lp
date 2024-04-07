"""
An abstract search algorithm class so that both Minimax and UCT can be made
to enforce the same interface.

Author: Khoi Nguyen
"""

from numpy.random import RandomState
from synthetic_games.games.crit_game import CritGame

from synthetic_games.games.game import Game


class BaseAlgorithm:
    """ An abstract search algorithm class for inheritance """

    def __init__(self, game, random_seed):
        self.game:CritGame = game
        self.randomness_source = RandomState(random_seed)

    def get_result(self):
        raise NotImplementedError()
