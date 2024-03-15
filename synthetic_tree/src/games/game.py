from typing import Dict


class Game:
  """Abstract game class"""
  def get_new_state(self, state: int, move: int) -> int:
    raise NotImplementedError
  
  def get_eval(self, state: int) -> float:
    raise NotImplementedError
    
  # def get_result(self, move: int) -> int:
  #   """ 
  #   Context: from the root node, a player makes move.
  #   Return: the minimax value of the next state.
  #   """
  #   state = self.get_new_state(1, move)
  #   print('hello')
  #   return self._get_node(state)['minimax']

  def _get_node(self, state: int) -> Dict:
    raise NotImplementedError
  
  def is_terminal(self, state: int) -> bool:
    # Default: infinitely deep
    raise NotImplementedError