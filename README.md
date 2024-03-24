# Lookahead Pathology in Monte Carlo Tree Search

This code base accompanies the paper '_Lookahead Pathology in Monte Carlo Tree Search_', published in ICAPS 2024. Please read the README in each of the folder `real_games` and `synthetic_tree` for further details.

## Critical Win-Loss Game

To generate each subplot Figure 4 in the paper, run:
```bash
# Firstly assign values for $B_FACTOR, $FLIP_RATE, $HEURISTIC
# ...

# Run experiment
python -m src.main figure4-$B_FACTOR-$FLIP_RATE-$HEURISTIC \
  --b-factor $B_FACTOR \
  --game-type crit \
  --flip-rate $FLIP_RATE $FLIP_RATE \
  --heuristic $HEURISTIC \
  --game-depth 50 \
  --algo-set uct \
  --num-games 500
```

Grid:
- `B_FACTOR: [2, 5, 8]`
- `FLIP_RATE: [0.9, 1]`
- `HEURISTIC: [chess-rand-10, chess-pseu-10]`

Results are in CSV files in `logs/default-batch`.

To make use of multiple CPUs, we actually split the jobs above into smaller jobs via the `num-games` arguments, then concatenated their results together.

## Cite

BibTeX entry
```
@misc{nguyen2022lookahead,
      title={Lookahead Pathology in Monte-Carlo Tree Search}, 
      author={Khoi P. N. Nguyen and Raghuram Ramanujan},
      year={2022},
      eprint={2212.05208},
      archivePrefix={arXiv},
      primaryClass={cs.AI}
}
```
