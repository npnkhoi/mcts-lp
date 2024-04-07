"""
A class to generate new abstract games

Author: Khoi Nguyen
"""

from typing import Dict
from numpy.random import RandomState
from synthetic_games.games.constants import Side
from synthetic_games.games.game import Game
from synthetic_games.games.constants import Side
from synthetic_games.heuristics.base import BaseHeuristic

class CritGame(Game):
  """ 
  A +1/-1 synthetic tree to generate new abstract games. 
  flip_rate=(MAX's, MIN's)
  In fixed game, move 0 is optimal everywhere.
  """

  def __init__(self, flip_rate=(1, 1), b_factor=2, depth=200, random_seed=None, verbose=False, fixed_game=False):
    # Set parameters of the game tree
    assert flip_rate[0] <= flip_rate[1]
    if fixed_game:
      assert flip_rate == (1, 1)
    
    self.flip_rate = flip_rate
    self.branching_factor = b_factor
    self.depth = depth
    self.randomness_source = RandomState(random_seed)
    self.fixed_game = fixed_game # if true, always let the first children to be 
    self.verbose = verbose

    # Define root node.
    root_node = dict(
      side=Side.MAX,
      depth=0,
      minimax=1,
      optimal_move=0 if self.fixed_game else \
        self.randomness_source.randint(0, self.branching_factor),
      heuristic=None, # never access the heuristic of root node
      flip_rate=1, # root node always have fr=1
      child_id={},
      move_at_root=None
    )
    assert root_node['optimal_move'] < self.branching_factor
    self._state_to_node = {1: root_node}
  
  def set_heuristic(self, heuristic_obj: BaseHeuristic):
    """Set heuristic object"""
    self.heuristic_obj = heuristic_obj
  
  def get_eval(self, state: int) -> float:
    """
    Get the heuristic value of a state AFTER it is created
    Heuristic range: [0, 1]
    """
    node = self._get_node(state)

    if node['heuristic'] is None: # not calculated yet (default)
      if self.is_terminal(state):
        heuristic = int(node['minimax'] > 0) # return true value
      else:
        heuristic = self.heuristic_obj.get_eval(game=self, node_id=state)
      self._state_to_node[state]['heuristic'] = heuristic
    
    assert 0 <= node['heuristic'] <= 1
    return self._get_node(state)['heuristic'] 

  def get_new_state(self, state: int, move: int):
    """ Return state ID after a move. May creating the new node. """
    # print(f"getting new state {state} {move}")
    assert move >= 0 and move < self.branching_factor
    if self.is_terminal(state):
      return None

    old_node = self._state_to_node[state]
    if move in old_node['child_id']:
      new_state = old_node['child_id'][move]
    else:
      new_state = len(self._state_to_node) + 1 # creating new node ID (increment)
      old_node['child_id'][move] = new_state
      self._state_to_node[new_state] = self._get_new_node(old_node, move)
      if self.verbose:
        print(f'INFO: Created new node {state} -> {new_state} with minimax {self._get_node(new_state)["minimax"]}')
    return new_state

  def is_terminal(self, state: int) -> bool:
    node = self._get_node(state)
    return node['depth'] == self.depth
  
  def _is_choice_node(self, node: Dict) -> bool:
    return node['minimax'] == node['side']

  def _is_pathological_move(self, state, move) -> bool:
    assert state != 1
    assert self.flip_rate == (1, 1)
    assert state in self._state_to_node
    node = self._get_node(state)
    assert self._is_choice_node(node)
    new_state = self.get_new_state(state, move)
    new_node = self._get_node(new_state)
    
    if node['move_at_root'] == 0:
      # (+) branch, wants (-) for pathology
      return new_node['minimax'] == -1
    else:
      return new_node['minimax'] == +1
  
  def _get_node(self, state):
    """ Return the node corresponding to a state ID """
    return self._state_to_node[state]

  def _get_new_node(self, old_node: Dict, move: int) -> Dict:
    """ Return a new node for a move """
    # Decide flipping and new minimax
    if (not self._is_choice_node(old_node)) or (move == old_node['optimal_move']):
      # forced node, losing or optimal move
      flip = False
    else:
      flip = self.randomness_source.random_sample() < old_node['flip_rate']
        
    new_minimax = old_node['minimax'] * (-1 if flip else 1)
    new_depth = old_node['depth'] + 1
    new_side = -old_node['side']
    new_flip_rate = self.flip_rate[0 if new_side == Side.MAX else 1]
    optimal_move = 0 if self.fixed_game \
      else self.randomness_source.randint(0, self.branching_factor)
    move_at_root = move if old_node['move_at_root'] == None \
      else old_node['move_at_root']
    
    assert optimal_move < self.branching_factor

    return dict(
      side=new_side,
      depth=new_depth,
      minimax=new_minimax,
      optimal_move=optimal_move,
      heuristic=None,
      flip_rate=new_flip_rate,
      child_id={},
      move_at_root=move_at_root
    )