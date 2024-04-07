"""
stockfish is a package downloaded from https://github.com/zhelyabuzhsky/stockfish.
It handles communicating directly with stockfish GUI, and can be extend to any chess engine.
Useful methods:
  _put(): write to GUI
  _read_line(): read 1 line from GUI
  set_position(moves: List[str]): set the engine to a position
  get_evaluation(): get the evaluation
  set_depth(depth: int): set depth so search command

This file implements Engine, an extension of Stockfish to fit our use.
"""

from typing import Dict, Optional
from real_games.chess_game.src.stockfish.stockfish import Stockfish
from random import choice

class Engine(Stockfish):
  """ Client to communicate (write and read) with stockfish engine (executable format) """
      
  def get_eval_pos(self, position):
    """
      Retuns: (object) evaluation of the current position in centipawns
      Output format: {type: "cp"/"mate", value: ...}

      Make an alpha-beta search with depth=self.depth
    """
    self.set_position(position)
    return self.get_evaluation()

  def next_moves(self):
    """ Return: a list of string as legal moves of the current position"""
    self._put("go perft 1")
    next_moves = []
    while True:
      line = self._read_line()
      if line == "":
        continue
      first_token = line.split(' ')[0]
      if first_token == 'Nodes':
        break
      next_moves.append(first_token[:-1])
    return next_moves
  
  def random_position(self, depth, n_top_moves, generation_search_depth=20, has_children: bool=False) -> Dict:
    """
    Params:
    - `n_top_moves`: If this is non-zero, at each move, 
      only that number of best moves are randomly chosen. 
      Otherwise, all legal moves are sampled.
    - `has_children`: whether the generated position must have at least one child
    - `generation_search_depth`: depth of search to find top moves
    
    Return: a random position at the specified depth
    
    The game will be set to the resulted position.
    """
    depth += int(has_children)
    
    old_depth = self.depth
    self.set_depth(generation_search_depth)
    # ^ Temporarily set search depth to this number (for faster running time)

    while True:
      moves = []
      success = True
      
      for _ in range(depth):
        self.set_position(moves) 
        # pick a random move from either (1) legal moves or (2) some best moves
        try:
          next_move = (choice(self.next_moves()) if n_top_moves == 0 \
            else choice(self.get_top_moves(n_top_moves))["Move"])
        except IndexError: # no moves next
          success = False
          break

        moves.append(next_move)
      
      if success:
        break
    self.set_depth(old_depth)
 
    if has_children:
      moves = moves[:-1]
    
    self.set_position(moves)
    fen = self.get_fen_position()

    return {
      'moves': moves, # list of str
      'fen': fen
    }
  
  def _go_nodes(self, nodes: int) -> None:
        self._put(f"go nodes {nodes}")

  def get_best_move_nodes(self, nodes: int = 1000) -> Optional[str]:
        """Returns best move with current position on the board by searching for a numder of nodes
        Args:
            nodes:
              Nodes for engine to determine best move
        Returns:
            A string of move in algebraic notation or None, if it's a mate now.
        """
        self._go_nodes(nodes)
        last_text: str = ""
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "bestmove":
                if splitted_text[1] == "(none)":
                    return None
                self.info = last_text
                return splitted_text[1]
            last_text = text