"""
Implementation of Upper Confidence bounds applied to Trees (UCT)

Author: Khoi Nguyen
"""
from typing import Dict
from src.games.constants import Side
from src.games.game import Game
from src.games.crit_game import CritGame
from src.algos.base import BaseAlgorithm
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
    
    def __init__(self, game: CritGame, bias_constant, num_iterations, random_seed=None):
        BaseAlgorithm.__init__(self, game, random_seed)
        self.root = UCTNode(state=1, side=Side.MAX, children={})
        if num_iterations < self.game.branching_factor:
            raise Exception("num_iterations must exceeed game's branching factor.")
        self.num_iterations = num_iterations # the number of nodes to expand
        self.bias_constant = bias_constant  # the constant c in UCB1 formula
        self.node_count = 0
        self.latest_expansion = None
        self.decisions = []
        sys.setrecursionlimit(100005) # NOTICE: how much should this be?

    def run(self) -> list[int]:
        """ 
        This function proceeds the iteration for a number of times.
        Returns a list of moves after the iterations.
        """

        self.node_count = 1
        self.decisions = []
        # Repeat the UCT iterations
        for iter in range(self.num_iterations):
            self._uct_recurse(self.root)
            
            # Get the best move from the root node
            move = self._select_move(node=self.root, bias_constant=0)
            self.decisions.append(move)

        return self.decisions

    def _uct_recurse(self, node: UCTNode) -> int:
        """
        Recursive method to proceed UCT iteration
        """

        # Select the best move to explore
        move = self._select_move(node, self.bias_constant)

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
    
    def _break_tie(self, node: UCTNode, moves: list) -> int:
        return self.randomness_source.choice(moves)

    def _select_move(self, node: UCTNode, bias_constant: float) -> int or None:
        """ 
        Return the best child to visit next according to UCB1 algorithm
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

            return self._break_tie(node, best_moves)
        else:
            # At least one child is unvisited -- cannot apply UCB1 formula
            # => Choose one random move
            new_moves = []
            for move in range(self.game.branching_factor):
                if move not in node.children:
                    new_moves.append(move)
            return self._break_tie(node, new_moves)

    def _expand(self, node, move):
        """ 
        Context: from a node (as well as a state), 
                 the algorithm tries making a move
        This method expands a new node on UCT tree for that move and return the 
        ultility of the new state
        """

        self.node_count += 1
        new_state = self.game.get_new_state(node.state, move)
        self.latest_expansion = new_state
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
