"""Script to run many games for a set of algorithms, in one certain setting"""

from typing import List
from numpy import random
from src.algos.constants import ALGOS
from src.heuristics.utils import HEURISTICS, create_heuristic
from src.games.game import Game
from src.utils import get_data, get_pgame, save_data
from src.algos.uct import UCTPlayer
from src.algos.alphabeta import AlphaBetaPlayer
from src.games.crit_game import CritGame
import os
import subprocess
import pandas
import time
import matplotlib.pyplot as plt
import click
from func_timeout import func_timeout, FunctionTimedOut


"""
Command template
    python -m src.main foo --game-type crit --flip-rate 1 1 --heuristic expected-playout --game-depth 51 --algo-set lite --num-games 5
    python -m src.main foo --game-type crit --flip-rate 1 1 --heuristic gaussian --stdev 0.1 --algo-set ab-sm --num-games 500 --b-factor 5
    python -m src.main foo --game-type hard --algo-set lite --num-games 5 --heuristic perfect
    python -m src.main foo --game-type p --game-depth 16 --algo-set lite --num-games 1 --heuristic mean-playout
"""
@click.command()
@click.argument('job-id', type=str)
@click.option('--batch-id', default='default-batch')
@click.option('--flip-rate', type=(float, float), default=(1, 1))
@click.option('--heuristic', type=click.Choice(HEURISTICS))
@click.option('--b-factor', type=int, default=2)
@click.option('--game-depth', type=int, default=10000)
@click.option('--reward', type=float, default=0) # FIXME: what is this?
@click.option('--punishment', type=float, default=0)
@click.option('--num-games', type=int, default='100')
@click.option('--timeout', type=int, default=1800, help='timeout for each search, in second unit')
@click.option('--algo-set', type=click.Choice(ALGOS.keys()), default='full')
@click.option('--confuse', type=float, help='Confusing rate for heuristic')
@click.option('--num-playouts', type=int, default=5, help='num playouts for sampled playout heuristics')
@click.option('--stdev', type=float, default=0.25, help='Stdev for Gaussian heuristic')
@click.option('--uniform-lower', type=float, default=-1.5, help='Lower bound for noise of Uniform heuristic')
@click.option('--uniform-upper', type=float, default=1.5, help='Upper bound for noise of Uniform heuristic')
@click.option('--game-type', type=click.Choice(['crit', 'hard', 'p']), default='crit', help='crit means the CWL game, p means P-games, hard means the artificially constructed game to make UCT pathological')
def main(job_id, batch_id, flip_rate, heuristic, b_factor, game_depth, \
    reward, punishment, num_games, timeout, algo_set, confuse, \
        num_playouts, stdev, uniform_lower, uniform_upper, game_type):
    # Create log directory
    path = os.path.join('logs', batch_id, job_id)
    subprocess.run(['mkdir', '-p', path])

    algos = ALGOS[algo_set]
    df_result = pandas.DataFrame(columns=algos)
    df_terminal = pandas.DataFrame(columns=algos)

    # Execute games
    for game_id in range(num_games):
        print(f'Game {game_id}/{num_games}')
        """INIT THE GAME: create the game, prepare variables"""
        if game_type in ['crit', 'hard']:
            game_class = CritGame if game_type == 'crit' else HardGame
            game:CritGame = game_class(depth=game_depth, flip_rate=flip_rate, b_factor=b_factor)
            game.set_heuristic(create_heuristic(heuristic, stdev=stdev))
        else:
            assert game_type == 'p'
            print('P-game')
            game = get_pgame(game_depth, b_factor)

        save_data(game, os.path.join(path, 'game')) # why?

        row_result = []
        row_terminal = []
        
        """RUN THE ALGORITHMS"""
        for algo in algos:
            print(f'Algo {algo}')
            game: Game = get_data(os.path.join(path, 'game'))
            params = algo.split('-')
            name = params[0]
            
            """UNPACK THE ALGO-CODE"""
            if name == 'rand':
                move = random.randint(0, b_factor)
            else:
                assert name in ['ab', 'uct']
                if name == 'ab':
                    player = AlphaBetaPlayer(game, random_seed=None, max_depth=int(params[1]))
                elif name == 'uct':
                    assert len(params) == 3
                    player = UCTPlayer(game, random_seed=None, num_iterations=int(params[2]), \
                        bias_constant=float(params[1]))
                
                try:
                    result = func_timeout(timeout, player.get_result)
                    move = result['move']
                except FunctionTimedOut:
                    move = None
                    print('Timeout!')
            
            """GET RESULT"""
            if move is not None:
                new_state = game.get_new_state(1, move)
                verdict = int(game._get_node(new_state)['minimax'] == 1)
                row_result.append(verdict)
            else:
                row_result.append(None)
            
            # Get and reset terminal count
            # row_terminal.append(len(game.stat['terminal']))
            # game.stat['terminal'].clear()

            """RECORD THE GAME STATE"""
            save_data(game, os.path.join(path, 'game'))
        
        """SAVE TO DATAFRAMES"""
        print(f'result: {row_result}')
        # print(f'terminal: {row_terminal}')
        df_result.loc[game_id] = row_result
        # df_terminal.loc[game_id] = row_terminal


    """WRITE THE DATAFRAME TO CSV"""
    df_result.to_csv(os.path.join(path, 'result.csv'))
    # df_terminal.to_csv(os.path.join(path, 'terminal.csv'))
    os.system(f'rm {path}/game') # delete the game file
    experiment_params = {
        "job_id": job_id,
        "flip_rate": flip_rate,
        "heuristic": heuristic,
        "b_factor": b_factor,
        "game_depth": game_depth,
        "reward": reward,
        "punishment": punishment,
        "num_games": num_games,
        "timeout": timeout,
        "algo_set": algo_set,
        "confuse": confuse,
        "num_playouts": num_playouts,
        "stdev": stdev,
        "uniform_lower": uniform_lower,
        "uniform_upper": uniform_upper,
        "game_type": game_type
    }
    save_data(experiment_params, os.path.join(path, 'params'))
    print('Done, detail here:', experiment_params)

if __name__ == '__main__':
    tic = time.time()
    main()
    toc = time.time()
    print(toc - tic)
