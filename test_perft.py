"""Perft test for tiny-chess-01 engine."""
import sys
sys.path.insert(0, ".")
from source import parse_fen, legal_moves, do_move, do_move_fast, upd_cas, atk, find_king

def perft(b,cas,ep,side,d):
    """Count legal moves to depth d."""
    if d==0:return 1
    ms=legal_moves(b,cas,ep,side)
    if d==1:return len(ms)
    total=0
    for m in ms:
        nb,nep=do_move_fast(b,m,side,ep)
        nc=upd_cas(cas,m[0],m[1])
        total+=perft(nb,nc,nep,-side,d-1)
    return total

def perft_divide(b,cas,ep,side,d):
    """Perft with move breakdown."""
    ms=legal_moves(b,cas,ep,side)
    total=0
    for m in ms:
        nb,nep=do_move_fast(b,m,side,ep)
        nc=upd_cas(cas,m[0],m[1])
        n=perft(nb,nc,nep,-side,d-1)
        total+=n
        from source import uci
        print(f"  {uci(m)}: {n}")
    print(f"  Total: {total}")
    return total

tests=[
    ("Start", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
     {1:20, 2:400, 3:8902, 4:197281}),
    ("Kiwipete", "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
     {1:48, 2:2039, 3:97862}),
]

all_pass=True
for name,fen,expected in tests:
    b,cas,ep,side=parse_fen(fen)
    for d,exp in sorted(expected.items()):
        result=perft(b,cas,ep,side,d)
        status="PASS" if result==exp else "FAIL"
        if status=="FAIL":all_pass=False
        print(f"{name} d{d}: {result} (expected {exp}) [{status}]")
        if status=="FAIL":
            perft_divide(b,cas,ep,side,d)

if all_pass:
    print("\nAll perft tests PASSED!")
else:
    print("\nSome perft tests FAILED!")
    sys.exit(1)
