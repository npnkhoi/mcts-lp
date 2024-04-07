from synthetic_games.heuristics.base import BaseHeuristic
from synthetic_games.heuristics.empirical import EmpiricalHeuristic
from synthetic_games.heuristics.expected_playout import ExpectedPlayoutHeuristic
from synthetic_games.heuristics.simple import GaussianHeuristic, PerfectHeuristic, UniformHeuristic

EMPIRICAL_HEURISTICS = ['chess-rand-10', 'chess-pseu-10', 'othello-rand-10', 'othello-pseu-10']
SIMPLE_HEURISTICS = ['gaussian', 'zero', 'perfect']
PLAYOUT_HEURISTICS = ['mean-playout', 'expected-playout', 'sampled-playout']
HEURISTICS = PLAYOUT_HEURISTICS + EMPIRICAL_HEURISTICS + SIMPLE_HEURISTICS

def create_heuristic(name: str, **kwargs) -> BaseHeuristic:
  """Return a heuristic object"""
  if name == 'perfect':
    return PerfectHeuristic()
  elif name in EMPIRICAL_HEURISTICS:
    return EmpiricalHeuristic(name)
  elif name == 'gaussian':
    return GaussianHeuristic(kwargs['stdev'])
  elif name == 'uniform':
    return UniformHeuristic(kwargs['stdev'])
  elif name == 'expected-playout':
    return ExpectedPlayoutHeuristic()
  else:
    raise KeyError('Heuristic not found')