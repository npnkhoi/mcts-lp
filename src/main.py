"""
Script to run many games for a set of algorithms, in one certain setting

Command template
    python -m src.main foo --game-type crit --flip-rate 1 1 --heuristic expected-playout --game-depth 51 --algo-set lite --num-games 5
    python -m src.main foo --game-type crit --flip-rate 1 1 --heuristic gaussian --stdev 0.1 --algo-set ab-sm --num-games 500 --b-factor 5
    python -m src.main foo --game-type hard --algo-set lite --num-games 5 --heuristic perfect
    python -m src.main foo --game-type p --game-depth 16 --algo-set lite --num-games 1 --heuristic mean-playout
"""

from typing import List
from numpy import random
from src.algos.constants import ALGOS
from src.heuristics.utils import HEURISTICS, create_heuristic
from src.games.game import Game
from src.utils import get_data, get_pgame, save_data
from src.algos.uct import UCTPlayer
from src.algos.uct_minimax import UCTMinimaxPlayer
from src.algos.alphabeta import AlphaBetaPlayer
from src.games.crit_game import CritGame
import os
import subprocess
import pandas
import time
import click
# from func_timeout import func_timeout, FunctionTimedOut
import json


@click.command()
@click.argument('job-id', type=str)
@click.option('--batch-id', default='default-batch')

@click.option('--game-type', type=click.Choice(['crit', 'p']), default='crit', 
    help='crit means the CWL game, p means P-games, hard means the artificially constructed game to make UCT pathological')
@click.option('--flip-rate', type=(float, float), default=(1, 1), 
    help='Flip rate for the game. In the general case, we have two values for the two players.')
@click.option('--b-factor', type=int, default=2,
    help='Branching factor for the game.')
@click.option('--game-depth', type=int, default=10000,
    help='Depth of the game tree.')

@click.option('--algo-set', type=click.Choice(ALGOS.keys()), default='full')
@click.option('--heuristic', type=click.Choice(HEURISTICS))
@click.option('--stdev', type=float, default=0.25, help='Stdev for Gaussian heuristic')

@click.option('--num-games', type=int, default=1)
@click.option('--timeout', type=int, default=1800, help='timeout for each search, in second unit')

# @click.option('--reward', type=float, default=0) # FIXME: what is this?
# @click.option('--punishment', type=float, default=0)
# @click.option('--confuse', type=float, help='Confusing rate for heuristic')
# @click.option('--num-playouts', type=int, default=5, help='num playouts for sampled playout heuristics')
# @click.option('--uniform-lower', type=float, default=-1.5, help='Lower bound for noise of Uniform heuristic')
# @click.option('--uniform-upper', type=float, default=1.5, help='Upper bound for noise of Uniform heuristic')
def main(**kwargs):
    print(kwargs)
    # Create log directory
    log_path = os.path.join('logs', kwargs["batch_id"], kwargs["job_id"])
    subprocess.run(['mkdir', '-p', log_path])

    algos = ALGOS[kwargs["algo_set"]]
    all_results = {
        'args': kwargs,
        'games': []
    }

    # Execute games
    for game_id in range(kwargs["num_games"]):
        print(f'Game {game_id}/{kwargs["num_games"]}')
        current_game_result = {
            'id': game_id,
            'move_utilities': [],
            'players': []
        }
        
        # INIT THE GAME: create the game, prepare variables#
        if kwargs["game_type"] == 'crit':
            game:CritGame = CritGame(depth=kwargs["game_depth"], flip_rate=kwargs["flip_rate"], b_factor=kwargs["b_factor"])
            game.set_heuristic(create_heuristic(kwargs["heuristic"], stdev=kwargs["stdev"]))
        else:
            assert kwargs["game_type"] == 'p'
            game = get_pgame(kwargs["game_depth"], kwargs["b_factor"], kwargs["heuristic"])
        
        for move in range(kwargs["b_factor"]):
            state = game.get_new_state(1, move)
            current_game_result['move_utilities'].append(game._get_node(state)['minimax'])

        # save game for reuse
        save_data(game, os.path.join(log_path, 'game'))

        # RUN THE ALGORITHMS
        for algo in algos:
            print(f'Algo {algo}')
            game: Game = get_data(os.path.join(log_path, 'game'))
            """
            for alphabeta, algo is 'ab-<depth>'
            for uct, algo is 'uct-<bias_constant>-<num_iterations>'
            """
            algo_params = algo.split('-')
            name = algo_params[0]
            
            # UNPACK THE ALGO CODE
            assert name in ['uct_minimax']

            # TODO: update the code below to return list of decisions
            
            assert name in ['ab', 'uct', 'uct_minimax']
            if name == 'ab':
                raise NotImplementedError
                player = AlphaBetaPlayer(game, random_seed=None, max_depth=int(algo_params[1]))
            elif name == 'uct':
                raise NotImplementedError
                assert len(algo_params) == 3
                player = UCTPlayer(game, random_seed=None, num_iterations=int(algo_params[2]), \
                    bias_constant=float(algo_params[1]))
            else:
                assert name == 'uct_minimax'
                player = UCTMinimaxPlayer(game, random_seed=None, num_iterations=int(algo_params[2]), \
                    bias_constant=float(algo_params[1]))
            
            player.run()
            current_game_result['players'].append({
                'algo': algo,
                'decisions': list(map(int, player.decisions)) # for JSON serialization
            })

            # RECORD THE GAME STATE FOR REUSE
            save_data(game, os.path.join(log_path, 'game'))
        
        # SAVE TO DATAFRAMES
        all_results['games'].append(current_game_result)


    # Save the results
    # breakpoint()
    with open(os.path.join(log_path, 'results.json'), 'w') as f:
        json.dump(all_results, f, indent=2)
    os.system(f'rm {log_path}/game') # delete the game file
    print('Done')

if __name__ == '__main__':
    tic = time.time()
    main()
    toc = time.time()
    print('Total time:', toc - tic, 'seconds')
