# Lookahead Pathology in Monte Carlo Tree Search

This code base accompanies the paper [Lookahead Pathology in Monte Carlo Tree Search](https://ojs.aaai.org/index.php/ICAPS/article/view/31501), published in ICAPS 2024. A [longer ArXiV version](https://arxiv.org/abs/2212.05208) includes extended experimental and theoretical results.

## Install

```bash
# From the root directory
pip install pipenv
pipenv shell
pipenv install
```

## Critical Win-Loss Game

To generate the data for each subplot Figure 5 in the paper, run:
```bash
# Firstly assign values for $B_FACTOR, $FLIP_RATE, $HEURISTIC
B_FACTOR=2
FLIP_RATE=1
HEURISTIC="chess-rand-10"

# Run experiment
python -m synthetic_games.main figure5-$B_FACTOR-$FLIP_RATE-$HEURISTIC \
  --b-factor $B_FACTOR \
  --game-type crit \
  --flip-rate $FLIP_RATE \
  --heuristic $HEURISTIC \
  --game-depth 50 \
  --algo-set uct \
  --num-games 500
```

Results are in CSV files in `logs/default-batch`. Parameter sets used in the paper are:
- `B_FACTOR: [2, 5, 8]`
- `FLIP_RATE: [0.9, 1]`
- `HEURISTIC: [chess-rand-10, chess-pseu-10]`

To make use of multiple CPUs, we actually split the jobs above into smaller jobs via the `num-games` arguments, then concatenated their results together.

To run a mini experiment, run the following
```bash
# Firstly assign values for $B_FACTOR, $FLIP_RATE, $HEURISTIC
B_FACTOR=2
FLIP_RATE=1
HEURISTIC="chess-rand-10"

# Run experiment
python -m synthetic_games.main tiny-$B_FACTOR-$FLIP_RATE-$HEURISTIC \
  --b-factor $B_FACTOR \
  --game-type crit \
  --flip-rate $FLIP_RATE \
  --heuristic $HEURISTIC \
  --game-depth 50 \
  --algo-set uct-tiny \
  --num-games 1
```

The results will be a JSON file as follows:
```json
{
  "args": { // all the arguments of the experiment
    // ...
  },
  "games": [ // `num_games` elements, each is a game instance
    {
      "id": 0, // game's index
      "move_utilities": [1, -1], // true utility of all move from the root node, from 0 to B_FACTOR-1
      "players": [ // results of all algorithms run on the current game
        {
          "algo": "uct-1-10", // name code of the algorithm
          "decisions": [ // the decision at root of UCT after each iteration
            0, 1, 1, 0, 0, 1, 1, 1, 1, 1
          ]
        }
      ]
    }
  ]
}
```

## Data collection on real games

Figure 3 and 4 in the main paper are results collected on real games -- Chess and Othello. General command for data collection is:

```bash
python -m [game].src.main [objective] [folder] [file] --n-positions=... --position-depth=... --n-top-moves=... --search-depth
```

For each game, we have put the game engine's binary file in the respective folders.

### Chess

Mini examples

```bash
python -m real_games.chess_game.src.main criticality chess criticality \
    --n-positions=1 \
    --position-depth=2 \
    --n-top-moves=0 \
    --search-depth=5

python -m real_games.chess_game.src.main noise chess noise \
    --n-positions=1 \
    --position-depth=2 \
    --n-top-moves=0 \
    --search-depth=5
```

### Othello

Mini examples
```bash
python -m real_games.othello.src.main noise othello noise \
    --n-positions=1 \
    --position-depth=2 \
    --n-top-moves=0 \
    --search-depth=5

python -m real_games.othello.src.main criticality othello criticality \
    --n-positions=1 \
    --position-depth=2 \
    --n-top-moves=0 \
    --search-depth=5
```


## Cite

If you find the code or results useful for your research, please cite our work as follows:
```
@article{Nguyen_Ramanujan_2024, 
  title={Lookahead Pathology in Monte-Carlo Tree Search}, 
  volume={34}, 
  url={https://ojs.aaai.org/index.php/ICAPS/article/view/31501}, 
  DOI={10.1609/icaps.v34i1.31501}, 
  number={1}, 
  journal={Proceedings of the International Conference on Automated Planning and Scheduling}, 
  author={Nguyen, Khoi P. N. and Ramanujan, Raghuram}, 
  year={2024}, 
  month={May}, 
  pages={414-422}
}
```
