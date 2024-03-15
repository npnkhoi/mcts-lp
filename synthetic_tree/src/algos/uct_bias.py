from src.algos.uct import UCTNode, UCTPlayer
from src.games.crit_game import CritGame
from src.games.game import Game
from src.heuristics.simple import PerfectHeuristic


class UCTBiasPlayer(UCTPlayer):
    """
    New things from standard player:
    - can control the probability to choose between 
    """
    def __init__(self, game: CritGame, bias_constant, num_iterations, pathology_bias: float, random_seed=None):
        self.pathology_bias = pathology_bias
        assert 0 <= pathology_bias <= 1
        super().__init__(game, bias_constant, num_iterations, random_seed)
    
    def _break_tie(self, node: UCTNode, moves: list) -> int:
        state = node.state
        _node = self.game._get_node(state)
        if state != 1 and self.game._is_choice_node(_node):
            # pathologically break
            move_groups = [[], []]
            for move in moves:
                if self.game._is_pathological_move(state, move):
                    move_groups[1].append(move)
                else:
                    move_groups[0].append(move)
            
            group = 1 if self.randomness_source.uniform(0, 1) <= \
                self.pathology_bias else 0
            if len(move_groups[0]) == 0:
                group = 1
            elif len(move_groups[1]) == 0:
                return 0            
            assert len(move_groups[group]) > 0
            return self.randomness_source.choice(move_groups[group])
        else:
            return super()._break_tie(node, moves)

if __name__ == "__main__":
    game = CritGame(flip_rate=(1, 1), b_factor=3, fixed_game=True)
    p = UCTBiasPlayer(game, 2.0, 10, 0.3)
    game.set_heuristic(PerfectHeuristic())
    p.get_result()
    print('Done')