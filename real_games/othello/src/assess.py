"""
Assessment functions for Chess positions
"""

from typing import Dict
from othello.src.edax import Engine
from utils import Logger, parse_eval

def assess_criticality(engine: Engine, logger: Logger, position: Dict, search_depth):
  """
    Analyzes the number of flipping children, finds the rate that minimax value is flipped.
    The engine will evoke new game (`ucinewgame`) for each position.

    `position` is a dictionary which 1 required key (`fen`) 
    and 1 optional key (`moves`, mostly used for debugging)
  """
  
  engine.set_position(position['moves'])
  logger.print(position['moves'])
  
  engine.set_depth(search_depth)
  score = engine.get_evaluation()
  logger.print(parse_eval(score))

  next_moves = engine.next_moves()
  if len(next_moves) != 0:
    engine.set_depth(search_depth-1) # decrease search depth for child nodes
    for next_move in next_moves:
      engine.set_position(position['moves'] + next_move)
      child_score = engine.get_evaluation()
      logger.print(parse_eval(child_score))

def assess_noise(engine: Engine, logger, position: Dict, depth):
  """
  Assess the static eval and search eval for a position. 
  Log 2 lines to logger: position and result

  The engine will evoke new game (`ucinewgame`) for each position.
  
  `position` is a dictionary which 1 required key (`fen`) 
  and 1 optional key (`moves`, mostly used for debugging)
  """
  engine.set_position(position['moves'])
  
  static_evaluation = engine.get_evaluation(search=False)
  search_evaluation = engine.get_evaluation(search=True)

  logger.print(position['moves'])
  logger.print(f'{parse_eval(static_evaluation)} {parse_eval(search_evaluation)}')
  return (static_evaluation, search_evaluation)