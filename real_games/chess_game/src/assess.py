"""
Assessment functions for Chess positions
"""

from typing import Dict
from chess_game.src.stockfish import Engine
from utils import parse_eval

def assess_criticality(engine: Engine, logger, position: Dict, search_depth):
  """
    Analyzes the number of flipping children, finds the rate that minimax value is flipped.
    The engine will evoke new game (`ucinewgame`) for each position.

    `position` is a dictionary which 1 required key (`fen`) 
    and 1 optional key (`moves`, mostly used for debugging)
  """
  
  engine.set_fen_position(position['fen'])
  logger.print(position['fen'])
  
  engine.set_depth(search_depth)
  score = engine.get_evaluation()
  logger.print(parse_eval(score))

  next_moves = engine.next_moves()
  if len(next_moves) != 0:
    engine.set_depth(search_depth-1) # decrease search depth for child nodes
    for next_move in next_moves:
      engine._put(f'position fen {position["fen"]} moves {next_move}')
      engine._start_new_game()
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
  engine.set_fen_position(position['fen'])
  
  engine._start_new_game()
  engine.set_depth(1)
  static_evaluation = engine.get_evaluation()
  
  engine._start_new_game()
  engine.set_depth(depth)
  search_evaluation = engine.get_evaluation()

  logger.print(position['fen'])
  logger.print(f'{parse_eval(static_evaluation)} {parse_eval(search_evaluation)}')
  return (static_evaluation, search_evaluation)

def assess_flipping_corelation(engine: Engine, logger, position: Dict, search_depth):
  """
    The engine will evoke new game (`ucinewgame`) for each position.

    `position` is a dictionary which 1 required key (`fen`) 
    and 1 optional key (`moves`, mostly used for debugging)
  """
  
  engine.set_fen_position(position['fen'])
  logger.print(position['fen'])
  
  engine.set_depth(search_depth)
  score = engine.get_evaluation()
  logger.print(parse_eval(score))
  logger.print('Children')

  next_moves = engine.next_moves()
  if len(next_moves) != 0:
    engine.set_depth(search_depth-1) # decrease search depth for child nodes
    for next_move in next_moves:
      engine._put(f'position fen {position["fen"]} moves {next_move}')
      engine._start_new_game()
      child_score = engine.get_evaluation()
      logger.print(f'{next_move} {parse_eval(child_score)}')
  
  logger.print('Grand children')
  engine.set_depth(search_depth-2)
  for next_move in next_moves:
    logger.print(f'First move = {next_move}')
    engine._put(f'position fen {position["fen"]} moves {next_move}')
    next_next_moves = engine.next_moves()
    for next_next_move in next_next_moves:
      engine._put(f'position fen {position["fen"]} moves {next_move} {next_next_move}')
      engine._start_new_game()
      grand_child_score = engine.get_evaluation()
      logger.print(parse_eval(grand_child_score))