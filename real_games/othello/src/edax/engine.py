import os
import subprocess
from typing import Dict, List
from random import choice

class Engine():
  def __init__(self, depth=20):
    """Import the engine executable"""
    
    FILENAME = './lEdax-x64-custom'
    DIR = os.path.join('real_games', 'othello', 'src', 'edax')

    self.engine = subprocess.Popen(
        FILENAME, universal_newlines=True, stdin=subprocess.PIPE, \
          stdout=subprocess.PIPE, cwd=DIR
    )
    self._output()  
    self._put('init')
    self._put(f'set level {depth}')
    self.depth = depth
    self.position = self.current_position()
  
  """--------------------- PUBLIC FUNCTIONS ---------------------"""

  def set_position(self, position: str) -> None:
    """
    Set the board to the `position`. `position` is moves.
    `self.position` will also hold next moves, past board and future board.
    This should be the only method that change the board's state.
    """
    self._put('init')
    self._put(f'play {position}')
    self.position = self.current_position()

  def set_depth(self, depth: int) -> None:
    """
    Set the depth of the search to `depth`
    """
    self.depth = depth
    self._put(f'set level {depth}')

  def current_position(self) -> Dict:
    """Return current position"""
    output = self._put('book show')

    past_board, future_board = [], []
    for line in output[-9:-1]:
      past_board.append(line.split('|')[-9:-1])
      future_board.append(line.split(' ')[1:9])
    
    moves = self._past_board_to_moves(past_board)
    next_moves = self._future_board_to_next_moves(future_board)
    
    return {
      'past': past_board,
      'future': future_board,
      'moves': moves,
      'next_moves': next_moves
    }
  
  def get_evaluation(self, search=True) -> Dict:
    """
    Return evaluation of the current position.
    from the perspective of the first player to move.
    Return format: `{type: value}`

    The evaluation must be reproducible
    """
    if len(self.position['next_moves']) == 0:
      # Game over
      count_white = sum(line.count('O') for line in self.position['future'])
      score = 64 if count_white > 0 else -64
    else:
      if search:
        # Search evaluation
        output = self._put('hint')
        verdict = output[3].split()[1]
        score = (1 if verdict[0] == '+'else -1) * int(verdict[1:])
      else:
        # Static evaluation
        output = self._put('eval')
        # print(output)
        score = int(output[1].strip().split()[2])

      assert abs(score) <= 64

      depth = len(self.position['moves']) // 2
      if depth % 2 == 1:
        score = -score
      

    return {
      'type': 'score',
      'value': score
    }
  
  def random_position(self, depth: int, n_top_moves: int = 0, \
    generation_search_depth: int = 10, has_children: bool = False) -> Dict:
    """
    Return a random position.
    Format: {type: position_string}
    """
    old_depth = self.depth
    self.set_depth(generation_search_depth)

    while True:
      self.set_position('')
      success = True
      for _ in range(depth + has_children):
        if len(self.position['next_moves']) == 0:
          success = False
          break
        next_move = (choice(self.position['next_moves'])
          if n_top_moves == 0
            else choice(self.top_next_moves(n_top_moves)))
        # print(f'Next move: {next_move}')
        self.set_position(self.position['moves'] + next_move)
        # print(f'Pos: {self.position["moves"]}')
      
      if success:
        break
    
    if has_children:
      self.set_position(self.position['moves'][:-2])
      assert len(self.position['moves']) == 2 * depth
    
    self.set_depth(old_depth) # return the old search depth

    return self.position

  def next_moves(self) -> List[str]:
    return self.position['next_moves']

  def top_next_moves(self, num_top_moves: int) -> List[str]:
    num_top_moves = min(num_top_moves, len(self.position['next_moves']))
    output = self._put(f'hint {num_top_moves}')
    # for line in output:
    #   print(line)
    FIRST_HINT = 3
    next_moves = []
    for row in range(FIRST_HINT, FIRST_HINT + num_top_moves):
      PV_POSITION = 52
      # print(output[row][PV_POSITION:])
      next_move = output[row][PV_POSITION:].split()[0]
      next_move = next_move[0].upper() + next_move[1] # capitalize the move
      next_moves.append(next_move)
    # print(f'Top moves: {next_moves}')
    return next_moves      

  """--------------------- PRIVATE FUNCTIONS ---------------------"""
  def _put(self, command: str) -> None:
    """
    Send `command` to the engine's GUI

    Copied completely from `python-stockfish`
    """
    if not self.engine.stdin:
        raise BrokenPipeError()
    self.engine.stdin.write(f"{command}\n")
    # print(f'> {command}')
    self.engine.stdin.flush()
    return self._output()
  
  def _read_line(self) -> str:
    if not self.engine.stdout:
      raise BrokenPipeError()
    return self.engine.stdout.readline()
  
  def _output(self):
    output = []
    BOARD_BORDER = '  A B C D E F G H'
    count_border = 0
    while True:
      line = self._read_line()
      # print(f'verdict: {line}')
      output.append(line)
      if line.startswith(BOARD_BORDER) \
        and ('BLACK' in line or 'WHITE' in line):
        count_border += 1
        if count_border == 2:
          # read 1 remaining line
          self._read_line()
          break
    if ('Game over' in output[-6]):
      self._read_line()
      self._read_line()
    return output

  def _cell_index_to_notation(self, row, col):
    return f'{chr(col + ord("A"))}{row+1}'

  def _past_board_to_moves(self, board) -> str:
    moves = ['' for _ in range(60)]
    for row in range(8):
      for col in range(8):
        cell = board[row][col].strip()
        if (cell.isnumeric()):
          idx = int(cell)
          moves[idx-1] = self._cell_index_to_notation(row, col)
    return ''.join(moves)

  def _future_board_to_next_moves(self, board) -> List[str]:
    next_moves = []
    for row in range(8):
      for col in range(8):
        if board[row][col] == '.':
          next_moves.append(self._cell_index_to_notation(row, col))
    return next_moves

