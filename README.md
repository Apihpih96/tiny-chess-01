# tiny-chess-01

A chess engine in a 4 KB Python file. Plays the make.fun tiny-chess-01 gauntlet
against 6 house engines (depth-2 through nodes-500k).

## Engine

- Fixed-depth alpha-beta negamax (depth 3) with MVV-LVA move ordering
- Piece-square table evaluation (material + positional bonuses)
- Integer board representation (64 squares, pieces as signed ints)
- Full legal move generation with castling, en passant, and promotions
- Deterministic: no clocks, no randomness, same moves on replay

## How to run

```bash
makefun grade-local --kit <kit-dir> --bot . --driver docker
```

Or with the trial runner:
```bash
~/workspace/makefun/tiny-chess-01-trial.sh . 0 8080
```

## Building

`main.py` is produced by compressing `source.py`:
```bash
makefun compress source.py --out main.py
```
