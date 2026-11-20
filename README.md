# tiny-chess-01

[![make.fun](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/Apihpih96/tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/Apihpih96/tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01)

A chess engine in 4 KB of Python, built for the [tiny-chess-01 bounty](https://make.fun/bounty/tiny-chess-01) on make.fun. It plays the gauntlet of 8 house engines (depth-2 through nodes-500k) through the make.fun env.

## Engine

- Iterative deepening alpha-beta negamax, fixed 80,000-node budget
- Quiescence search (captures, promotions, check extensions)
- Null-move pruning (R=2), late move reductions, aspiration windows
- MVV-LVA + killer/history move ordering
- Piece-square table evaluation: material, bishop pair, passed pawns, pawn structure (doubled/isolated), king safety
- Full legal move generation: castling, en passant, promotions
- Deterministic: no clocks, no randomness, same moves on replay
- Practice Elo 876 (0W 2D 4L on each of the 3 practice trials)

## Run

The env runs it as `python3 -P -s main.py` (Python 3.13, stdlib only).
`main.py` is produced by compressing the readable `source.py` with the kit:

```bash
node <kit>/cli/makefun.mjs compress source.py --out main.py
```

Referral code: `qv9aepwe`
