from synthetic_games.games.game import Game
from synthetic_games.heuristics.base import BaseHeuristic


class ExpectedPlayoutHeuristic(BaseHeuristic):
  def get_eval(self, game: Game, node_id: int) -> float:
    """
    Return expected value of the leaves in the subtree rooted at the current node
    """
    node = game._get_node(node_id)
    minimax = node['minimax']
    depth = node['depth']
    side = node['side']

    def f(rem_depth):
        """f() function in the paper"""
        assert rem_depth > 0
        c1, c2 = game.flip_rate
        b = game.branching_factor

        k1 = 1 - c1 + c1 / b
        k2 = 1 - c2 + c2 / b
        d = rem_depth // 2
        k_product = k1 * k2
        
        if d == 0:
            ret = 1
        else:
            ret = (k_product) ** d + (1 - k2) * (1 - k_product ** (d + 1)) / (1 - k_product)
        if rem_depth % 2 != 0:
            ret = ret * k1
        assert 0 <= ret and ret <= 1
        return ret
    
    tree_depth = game.depth

    # If forced node, calculate the child
    if minimax != side:
        depth += 1
        side = -side
        # minimax remains
        # no need to revert anything onwards
        
        if depth == tree_depth:
            return int(minimax > 0)

    win_rate = f(tree_depth - depth)
    ret = (win_rate * 2 - 1) * minimax # flip the sign for -1 node
    ret = (ret + 1) / 2 # scale from [-1, 1] to [0, 1] for UCT
    ROUNDING_FACTOR = 6
    ret = round(ret, ROUNDING_FACTOR)
    return ret

"""
def _get_sampled_playout(self, minimax, depth, side):
    expected = self._get_expected_playout(minimax, depth, side)
    plus_density = (expected + 1) / 2
    heuristic = 0
    for _ in range(self.params['num_samples']):
        sample = random.uniform(0, 1)
        playout = (+1 if sample < plus_density else -1)
        heuristic += (playout > 0) # bring to scale [0, 1]
    heuristic /= self.params['num_samples']
    return heuristic
"""