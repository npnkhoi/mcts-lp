"""Helpful functions to write logs and draw plots"""

class Logger:
  """
  Logger
  """
  def __init__(self, filepath):
    """Create a .txt file with the current timestamp"""
    self.file = open(filepath, 'w+')
    self.filepath = filepath

  def print(self, info):
    print(info, file=self.file)
  
  def close(self):
    print(f'Logged in {self.filepath}')
    self.file.close()

def parse_eval(eval: dict) -> str:
  """
  Return a string with the evaluation of the game
  """
  e_type = eval['type']
  value = eval['value']
  return f'{e_type} {value}'