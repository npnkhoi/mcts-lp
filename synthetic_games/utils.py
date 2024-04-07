import pickle

from synthetic_games.games.p_game import PGame


def get_data(filename: str) -> None:
    ''' Return an unpickled object from a file '''
    with open(filename, 'rb') as file:
        result = pickle.load(file)
    return result


def save_data(data, filename: str) -> None:
    ''' Pickle an object into a file '''
    with open(filename, 'wb+') as file:
        pickle.dump(data, file)


def get_pgame(depth, b,  heuristic):
    while True:
        game = PGame(depth=depth, b=b, heuristic=heuristic)

        flag = False
        for i in range(3, b+2):
            if game._state_to_node[2]['minimax'] != game._state_to_node[i]['minimax']:
                flag = True
                break

        if game._state_to_node[1]['minimax'] == +1 and flag:
            break
    
    return game