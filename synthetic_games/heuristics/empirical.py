import pickle
import numpy as np
from synthetic_games.heuristics.base import BaseHeuristic


class EmpiricalHeuristic(BaseHeuristic):
  def __init__(self, hist_name: str):
    with open('synthetic_games/heuristics/heuristic_data/'+hist_name+'.pkl', 'rb') as f:
      self.hist = pickle.load(f)
    self.min_heuristic = min(min(self.hist[0]), min(self.hist[1]))
    self.max_heuristic = max(max(self.hist[0]), max(self.hist[1]))
  
  def get_eval(self, game, node_id: int) -> float:
    """ Return heuristic based on histogram of real game data """
    minimax = game._get_node(node_id)['minimax']
    sample = np.random.choice(self.hist[minimax > 0])
    # normalize into [0, 1]
    ret = (sample - self.min_heuristic) / (self.max_heuristic - self.min_heuristic)
    return ret