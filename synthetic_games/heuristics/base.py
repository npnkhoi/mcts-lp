"""Heuristic class"""

from synthetic_games.games.game import Game

class BaseHeuristic:
  def get_eval(self, game: Game, node_id: int) -> float:
    raise NotImplementedError
