"""
Alphabeta search algorithm

"""

from src.algos.base import BaseAlgorithm
from src.games.constants import Side
from src.games.game import Game
from src.games.crit_game import CritGame


class AlphaBetaPlayer(BaseAlgorithm):
    INFINITY = 1e9

    def __init__(self, game: Game, max_depth=10, random_seed=None, random_flag=False):

        BaseAlgorithm.__init__(self, game, random_seed)
        if max_depth < 1:
            raise Exception("max_depth must be positive.")
        self.max_depth = max_depth
        self.random_flag = random_flag
        self.prune_count = 0
        self.node_count = 0

        # This field is to validate node_count, calculated via prunning events
        self.estimated_node_count = 0

    def branch_size(self, depth):
        """ 
        Return number of nodes in a uniform branch with given depth 
        Tree with only 1 node is considered as zero-depth
        """
        b = self.game.branching_factor
        return (b**(depth + 1) - 1) // (b - 1)

    def get_result(self):
        """ Return optimal move based on Minimax algorithm """

        # Initialize values for a call
        self.prune_count = 0
        self.node_count = 0
        self.estimated_node_count = self.branch_size(self.max_depth)

        result = self._alphabeta(state=1, depth_to_go=self.max_depth, side=Side.MAX.value)
        return {
            "move": result[1],
            "utility": result[0],
            "node_count": self.node_count,
            "prune_count": self.prune_count,
            "estimated_node_count": self.estimated_node_count
        }

    def _alphabeta(self, state, depth_to_go, side: Side, alpha=-INFINITY,
                   beta=INFINITY):
        """ 
        Return (estimated minimax value, best move) 
        [alpha, beta]: expectation window
        The minimax value found by this function call must be in the range 
        to be useful for the ultimate search process
        """
        self.node_count += 1

        if depth_to_go == 0:
            return (self.game.get_eval(state), None)

        # children: a randomly ordered list of child nodes
        children = [i for i in range(self.game.branching_factor)]
        if self.random_flag:
            self.randomness_source.shuffle(children)

        num_visited = 0 # number of visited children

        if side == Side.MAX.value:
            # Max's turn
            score = -self.INFINITY
            best_move = 0
            # recurse Minimax for next level
            for move in children:
                num_visited += 1
                eval = self._alphabeta(self.game.get_new_state(state, move),
                                       depth_to_go - 1, -side, alpha, beta)[0]
                if eval > score:
                    score = eval
                    best_move = move
                    alpha = max(alpha, score)

                if alpha >= beta:
                    # Pruning and update estimated_node_count
                    self.prune_count += 1
                    self.estimated_node_count -= (
                        self.branch_size(depth_to_go - 1)
                        * (self.game.branching_factor - num_visited)
                    )
                    break
            
            return (score, best_move)

        else:
            # Min's turn
            score = self.INFINITY
            best_move = 0
            # recurse Minimax for next level
            for move in children:
                num_visited += 1
                eval = self._alphabeta(self.game.get_new_state(state, move),
                                       depth_to_go - 1, -side, alpha, beta)[0]
                if eval < score:
                    score = eval
                    best_move = move
                    beta = min(beta, score)

                if beta <= alpha:
                    # Pruning and update estimated_node_count
                    self.prune_count += 1
                    self.estimated_node_count -= (
                        self.branch_size(depth_to_go - 1)
                        * (self.game.branching_factor - num_visited)
                    )
                    break
            
            return (score, best_move)
