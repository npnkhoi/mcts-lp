"""
  Runs multiple experiments, using stockfish engine.

  Output is logged to a log folder

  Command-line args: see the click arguments
"""

import subprocess
import click
from os.path import join
from real_games.othello.src.assess import assess_criticality, assess_noise
from real_games.utils import Logger
from real_games.othello.src.edax import Engine
import time

def init_logger(batch_id, job_id, objective, n_positions, position_depth, \
  search_depth, n_top_moves):
  
  base_path = join('logs', batch_id) 
  subprocess.run(['mkdir', '-p', base_path])
  filepath = join(base_path, job_id + '.txt')
  logger = Logger(filepath)
  title = f"""Othello
Objective: {objective}
Num positions: {n_positions}
Position depth: {position_depth}
Search depth: {search_depth}
Num top moves: {n_top_moves}
  """
  logger.print(title)
  return logger

OBJECTIVES = ['flip-grand', 'criticality', 'noise']

# python -m othello.src.main flip-grand big small
@click.command() 
@click.argument('objective', type=str)
@click.argument('batch-id', type=str)
@click.argument('job-id', type=str)
@click.option('--search-depth', type=int, default=20, \
  help="Search depth for Stockfish evaluation")
@click.option('--n-positions', type=int, default=2, \
  help='No. positions to analyze')
@click.option('--n-top-moves', type=int, default=0, \
  help='No. top moves to choose at each turn when generating positions. \
    Leave this 0 to create purely random games.')
@click.option('--position-depth', type=int, default=10, \
  help='Depth of generated positions')
@click.option('--generation-search-depth', type=int, default=10, \
  help='Depth of top-move search for position generation')
def run_exp(objective, batch_id, job_id, search_depth, n_positions, n_top_moves, position_depth, generation_search_depth):
  tic = time.time()
  logger = init_logger(batch_id, job_id, objective, n_positions, position_depth, search_depth, n_top_moves)
  engine = Engine()

  has_children = True
  if objective == 'criticality':
    assess = assess_criticality
    has_children = True
  elif objective == 'noise':
    assess = assess_noise

  for i in range(n_positions):
    position = engine.random_position(position_depth, \
      n_top_moves, generation_search_depth=generation_search_depth, \
        has_children=has_children)
    print(f'Position {i+1}/{n_positions}: {position["moves"]}')
    
    assess(engine, logger, position, search_depth)
    logger.print("END")
  
  logger.close()

  toc = time.time()
  print(f'{toc - tic} seconds')

if __name__ == "__main__":
  run_exp()