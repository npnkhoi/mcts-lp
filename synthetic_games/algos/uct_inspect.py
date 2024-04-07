"""
This is the clone of the original code, for the purpose of internal inspection during experiments.

Implementation of Upper Confidence bounds applied to Trees (UCT)

Author: Khoi Nguyen
"""
from typing import Dict
from synthetic_games.games.constants import Side
from synthetic_games.games.game import Game
from synthetic_games.games.crit_game import CritGame
from synthetic_games.algos.base import BaseAlgorithm
from dataclasses import dataclass
from math import sqrt, log
import sys

# Structure to store a node of the UCT search tree
@dataclass
class UCTNode:
    state: int
    side: Side
    children: Dict[int, dataclass]  # mapping: move -> node
    utility: float = 0.0
    visit_count: int = 0


class UCTPlayer(BaseAlgorithm):
    """ Class to play games by UCT algorithm """
    INFINITY = 1e9

    def __init__(self, game: Game, bias_constant, num_iterations, random_seed=None):
        BaseAlgorithm.__init__(self, game, random_seed)
        self.root = UCTNode(state=1, side=Side.MAX, children={})
        if num_iterations < self.game.branching_factor:
            raise Exception("num_iterations must exceeed game's branching factor.")
        self.num_iterations = num_iterations # the number of nodes to expand
        self.bias_constant = bias_constant  # the constant c in UCB1 formula
        self.node_count = 0
        
        sys.setrecursionlimit(100005) # NOTICE: how much should this be?
        
        self.bfs_flag = True
        self.explored_move_at_root = None

    def get_result(self):
        """ 
        This function proceeds the iteration for a number of times,
        then returns the best move based on estimated utility.
        This is the main function to communicate with the playing environment.
        """

        self.node_count = 1
        # Repeat the UCT iterations
        for _ in range(self.num_iterations):
            self._uct_recurse(self.root)

        move = self._select_move(node=self.root, bias_constant=0)
        return {
            "move": move,
            "utility": self.root.children[move].utility,
            "node_count": self.node_count
        }

    def _uct_recurse(self, node: UCTNode) -> int:
        """
        Recursive method to proceed UCT iteration
        """

        # Select the best move to explore
        move = self._select_move(node, self.bias_constant)
        if self.explored_move_at_root is None:
            self.explored_move_at_root = move
        # self.bfs_flag = True

        # Recurse or expand
        if move is None:
            # Encounter leaf node, result = heuristic value
            result = self.game.get_eval(node.state)
        elif move in node.children:
            result = self._uct_recurse(node.children[move])
        else:
            result = self._expand(node, move)

        # Backpropagrate
        node.visit_count += 1
        # utility: average of results over all iterations from that node
        # below is slightly different than the original formula, but actually correct
        node.utility += (result - node.utility) / node.visit_count 

        return result

    def _select_move(self, node: UCTNode, bias_constant: float) -> int:
        """ 
        Return the best child to visit next according to UCB1 algorithm
        Side effect: many turn self.bfs_flag to False
        """
        if self.game.is_terminal(node.state):
            return None
        elif len(node.children) == self.game.branching_factor:
            # All the children are visited.
            best_moves = []
            best_score = -node.side * self.INFINITY

                        
            for move in range(self.game.branching_factor):
                child = node.children[move]
                # UCB1 formula
                score = (child.utility + node.side * bias_constant *
                         sqrt(log(node.visit_count) / child.visit_count))
                if ((score > best_score and node.side == Side.MAX) 
                    or (score < best_score and node.side == Side.MIN)):
                    # Better move found
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)
            
            # DEBUGGING verify BFS-ness
            min_visit_count = min([child.visit_count for child in node.children.values()])
            for move in best_moves:
                if node.children[move].visit_count != min_visit_count:
                    self.bfs_flag = False


            return self.randomness_source.choice(best_moves)


        else:
            # At least one child is unvisited -- cannot apply UCB1 formula
            # => Choose one random move
            new_moves = []
            for move in range(self.game.branching_factor):
                if not move in node.children:
                    new_moves.append(move);
            return self.randomness_source.choice(new_moves)

    def _expand(self, node, move):
        """ 
        Context: from a node (as well as a state), 
                 the algorithm tries making a move
        This method expands a new node on UCT tree for that move 
        and return the ultility of the new state
        """

        self.node_count += 1
        new_state = self.game.get_new_state(node.state, move)
        result = self.game.get_eval(new_state)

        # Create a new node on UCT tree as a new child of the old node
        node.children[move] = UCTNode(
            state=new_state,
            side=-node.side,
            children={},
            utility=result,
            visit_count=1
        )

        return result
