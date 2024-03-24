"""
Pearl Game
FIXME: dont use Heuristic!
"""

from typing import Dict
from numpy import random
import math
from src.games.game import Game
from src.games.constants import Side
import scipy.optimize


class PGame(Game):
    def __init__(self, depth: int=20, b: int=2, heuristic='mean-playout'):
        self.depth = depth
        self.branching_factor = b
        self.heuristic_name = heuristic
        # self.heuristic_object = Heuristic(name=heuristic, depth=depth, branching_factor=b_factor)
        self._state_to_node = {}

        # set sample_constant to be the solution between 0 and 1 of the equation x^depth + x - 1 = 0
        equation = lambda x, b: (1-x)**b - x

        sample_constant = scipy.optimize.brentq(equation, 0, 1, args=(self.branching_factor)) # source: https://dl.acm.org/doi/abs/10.1145/3501714.3501723
        print('sample_constant:', sample_constant)

        # sample_constant = (math.sqrt(5) - 1) / 2 # taken from nau1982 paper
        
        num_nodes = (b ** (depth + 1) - 1) // (b - 1)
        num_leaves = b ** depth
        
        # Build the tree bottom up, right to left
        for i in range(num_nodes):
            state = num_nodes - i

            if i < num_leaves: # is a leaf
                side = Side.MAX.value if self.depth % 2 == 0 else Side.MIN.value

                # Randomly assign a value to the leaf based on sample_constant
                minimax= +1 if (random.uniform(0, 1) < sample_constant) else -1

                if side == Side.MAX.value: # why? check the paper
                    minimax *= -1

                node = dict(
                    minimax=minimax,
                    depth=self.depth,
                    side=side,
                    mean_playout=(minimax > 0),
                    heuristic=None
                )
            else: # is a internal node
                children = [self._state_to_node[state * b + i] for i in range(2-b, 2)]
                side = -children[0]['side']
                
                mean_playout = sum([child['mean_playout'] for child in children]) / b
                minimax_list = [child['minimax'] for child in children]
                    
                if side == Side.MAX.value:
                    minimax = max(minimax_list)
                else:
                    minimax = min(minimax_list)
                
                node = dict(
                    minimax=minimax,
                    depth=children[0]['depth']-1,
                    side=side,
                    mean_playout=mean_playout,
                    heuristic=None
                )
        
            self._state_to_node[state] = node
        # Done building tree

        # Stats
        self.stat = {
            'terminal': set()
        }

    def get_new_state(self, state: int, move: int) -> int:
        new_state = state * self.branching_factor + move - self.branching_factor + 2
        return new_state

    def get_eval(self, state: int) -> float:
        """Get the heuristic value of a state AFTER it is created"""
        node = self._get_node(state)
        if node['heuristic'] is None:
            self._state_to_node[state]['heuristic'] = self.get_heuristic(
                state, node['minimax'], node['depth'], node['side'])
        if self.is_terminal(state):
            self.stat['terminal'].add(state)
        return self._get_node(state)['heuristic']
    
    def get_heuristic(self, state, minimax, depth, side):
        """Get the heuristic value of a state WHILE it is being created"""
        if depth == self.depth: # for terminal nodes
            return int(minimax > 0)
            
        if self.heuristic_name == 'mean-playout':
            return self._state_to_node[state]['mean_playout']
        else:
            raise NotImplementedError('Heuristic not implemented')
    
    def _get_node(self, state: int) -> Dict:
        """
        Return: minimax and heuristic, at least
        """
        return self._state_to_node[state]

    def is_terminal(self, state: int) -> bool:
        return self._state_to_node[state]['depth'] == self.depth
