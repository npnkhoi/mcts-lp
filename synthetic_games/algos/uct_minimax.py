from synthetic_games.algos.uct import UCTPlayer, UCTNode
from synthetic_games.games.constants import Side


class UCTMinimaxPlayer(UCTPlayer):
    # Note: utility of root node is intialized to 0, but that doesn't matter because
    # it is updated at every iteration

    def _uct_recurse(self, node: UCTNode) -> int:
        """
        Recursive method to proceed UCT iteration

        This method is overridden to implement the minimax backpropagation instead of averaging the results.
        """

        # Select the best move to explore
        move = self._select_move(node, self.bias_constant)

        # Recurse or expand
        if move is None:
            # Encounter leaf node, result = heuristic value
            result = self.game.get_eval(node.state)
            node.visit_count += 1
            return result
        elif move in node.children:
            result = self._uct_recurse(node.children[move])
        else:
            result = self._expand(node, move)

        # Backpropagrate with minimax (instead of averaging)
        node.visit_count += 1
        if node.side == Side.MAX:
            # If the node is a MAX node, then the utility is the maximum of the children
            node.utility = max([child.utility for child in node.children.values()])
        else:
            # If the node is a MIN node, then the utility is the minimum of the children
            node.utility = min([child.utility for child in node.children.values()])

        return result