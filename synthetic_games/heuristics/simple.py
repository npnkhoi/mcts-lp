import numpy as np
from synthetic_games.games.game import Game
from synthetic_games.heuristics.base import BaseHeuristic
from synthetic_games.heuristics.empirical import EmpiricalHeuristic


class PerfectHeuristic(BaseHeuristic):
  def get_eval(self, game: Game, node_id: int) -> float:
    """Return the true minimax value"""
    minimax = game._get_node(node_id)['minimax']
    heuristic = (minimax + 1) // 2
    assert 0 <= heuristic <= 1
    return heuristic

class ZeroHeuristic(BaseHeuristic): # Not tested
  def get_eval(self, game: Game, node_id: int) -> float:
    """Return 0 :)"""
    return 0

class GaussianHeuristic(EmpiricalHeuristic):
  """
  Adding Gaussian noise into the true utility
  The heuristic values are already normalized into [0, 1]
  """
  def __init__(self, stdev: float, sample_size: int=10**5): 
    # Initialize a Gaussian distribution
    self.hist = [
        -1 + np.random.normal(0, stdev, size=sample_size),
        +1 + np.random.normal(0, stdev, size=sample_size)
    ]
    self.min_heuristic = min(min(self.hist[0]), min(self.hist[1]))
    self.max_heuristic = max(max(self.hist[0]), max(self.hist[1]))
  
  def get_eval(self, game, node_id: int) -> float:
    # Because we use historgram, we reuse the code of empirical heuristics
    return super().get_eval(game, node_id)

class UniformHeuristic(EmpiricalHeuristic):
  def __init__(self, stdev: float, sample_size: int=10**5): 
    # Initialize a Gaussian distribution
    self.hist = [
        -1 + np.random.uniform(0, stdev, size=sample_size),
        +1 + np.random.uniform(0, stdev, size=sample_size)
    ]
    self.min_heuristic = min(min(self.hist[0]), min(self.hist[1]))
    self.max_heuristic = max(max(self.hist[0]), max(self.hist[1]))
  
  def get_eval(self, game, node_id: int) -> float:
    # Because we use historgram, we reuse the code of empirical heuristics
    return super().get_eval(game, node_id)


"""
def _get_confused(self, minimax, depth, side):
  # Return heuristic after a probabilistic flipping
  sample = np.random.uniform(0, 1)
  multiplier = -1 if (sample < self.params['confuse']) else 1
  return minimax * multiplier
"""