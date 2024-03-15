General command

```bash
python -m [game].src.main [objective] [folder] [file] --n-positions=... --position-depth=... --n-top-moves=... --search-depth
```

For each game, we downloaded the binary of the game engine and put it in the respective folders.

## Chess

```bash
python -m chess_game.src.main criticality chess criticality \
    --n-positions=1 \
    --position-depth=2 \
    --n-top-moves=0 \
    --search-depth=5

python -m chess_game.src.main noise chess noise \
    --n-positions=1 \
    --position-depth=2 \
    --n-top-moves=0 \
    --search-depth=5
```

## Othello

```bash
python -m othello.src.main noise othello noise \
    --n-positions=1 \
    --position-depth=2 \
    --n-top-moves=0 \
    --search-depth=5

python -m othello.src.main criticality othello criticality \
    --n-positions=1 \
    --position-depth=2 \
    --n-top-moves=0 \
    --search-depth=5
```
