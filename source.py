"""tiny-chess-01 — depth-3+ engine with correct board copying."""
import json,os,sys,urllib.error,urllib.request

ENV=os.environ.get("MAKEFUN_ENV_URL")

# Piece values: idx 0..6 (none,P,N,B,R,Q,K)
V=[0,100,320,330,500,900,20000]

# Piece-square tables (white perspective, index = file + (7-rank)*8)
PP=[0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,0,0,0,0,0,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,5,10,10,-20,-20,10,10,5]
PN=[-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50]
PB=[-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,10,10,10,10,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20]
PR=[0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0]
PQ=[-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20]
PK=[-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20]
PS=[None,PP,PN,PB,PR,PQ,PK]

PM={"P":1,"N":2,"B":3,"R":4,"Q":5,"K":6,"p":-1,"n":-2,"b":-3,"r":-4,"q":-5,"k":-6}

ND=[-17,-15,-10,-6,6,10,15,17]
BD=[-9,-7,7,9]
RD=[-8,-1,1,8]
KD=[-9,-8,-7,-1,1,7,8,9]
NA=[[s+d for d in ND if 0<=s+d<64 and abs((s+d)%8-s%8)<=2]for s in range(64)]
KA=[[s+d for d in KD if 0<=s+d<64 and abs((s+d)%8-s%8)<=1 and abs((s+d)//8-s//8)<=1]for s in range(64)]

def mirror(s):return((7-s//8)*8+s%8)

def ev(b):
    e=0
    for s in range(64):
        p=b[s]
        if p==0:continue
        a=abs(p)
        v=V[a]+PS[a][s if p>0 else mirror(s)]
        e+=v if p>0 else-v
    return e

def atk(b,s,w):
    if w==1:
        for df in(-1,1):
            t=s+8+df
            if 0<=t<64 and abs(t%8-s%8)==1 and b[t]==1:return 1
        for t in NA[s]:
            if b[t]==2:return 1
        for d in BD:
            t=s
            while 1:
                t+=d
                if not(0<=t<64)or abs(t%8-((t-d)%8))>1:break
                if b[t]==3 or b[t]==5:return 1
                if b[t]!=0:break
        for d in RD:
            t=s
            while 1:
                t+=d
                if not(0<=t<64)or abs(t%8-((t-d)%8))>1:break
                if b[t]==4 or b[t]==5:return 1
                if b[t]!=0:break
        for t in KA[s]:
            if b[t]==6:return 1
    else:
        for df in(-1,1):
            t=s-8+df
            if 0<=t<64 and abs(t%8-s%8)==1 and b[t]==-1:return 1
        for t in NA[s]:
            if b[t]==-2:return 1
        for d in BD:
            t=s
            while 1:
                t+=d
                if not(0<=t<64)or abs(t%8-((t-d)%8))>1:break
                if b[t]==-3 or b[t]==-5:return 1
                if b[t]!=0:break
        for d in RD:
            t=s
            while 1:
                t+=d
                if not(0<=t<64)or abs(t%8-((t-d)%8))>1:break
                if b[t]==-4 or b[t]==-5:return 1
                if b[t]!=0:break
        for t in KA[s]:
            if b[t]==-6:return 1
    return 0

def find_king(b,side):
    target=6 if side==1 else-6
    for s in range(64):
        if b[s]==target:return s
    return 0

def gen_moves(b,cas,ep,side):
    ms=[]
    w=side==1
    for s in range(64):
        pc=b[s]
        if pc==0 or(pc>0)!=w:continue
        t=abs(pc)
        if t==1:
            d=-8 if w else 8
            sr=s//8
            tk=s+d
            if 0<=tk<64 and b[tk]==0:
                if(w and tk<8)or(not w and tk>55):
                    for x in(5,4,3,2):ms.append((s,tk,x*side,0))
                else:
                    ms.append((s,tk,0,0))
                    if(w and sr==6)or(not w and sr==1):
                        tk2=s+2*d
                        if 0<=tk2<64 and b[tk2]==0:ms.append((s,tk2,0,0))
            for df in(-1,1):
                tk=s+d+df
                if 0<=tk<64 and abs(tk%8-s%8)==1:
                    if b[tk]!=0 and(b[tk]>0)!=w:
                        if(w and tk<8)or(not w and tk>55):
                            for x in(5,4,3,2):ms.append((s,tk,x*side,0))
                        else:ms.append((s,tk,0,0))
                    if tk==ep:ms.append((s,tk,0,0))
        elif t==2:
            for tk in NA[s]:
                if b[tk]==0 or(b[tk]>0)!=w:ms.append((s,tk,0,0))
        elif t==3:
            for d in BD:
                tk=s
                while 1:
                    tk+=d
                    if not(0<=tk<64)or abs(tk%8-((tk-d)%8))>1:break
                    if b[tk]==0:ms.append((s,tk,0,0));continue
                    if(b[tk]>0)!=w:ms.append((s,tk,0,0))
                    break
        elif t==4:
            for d in RD:
                tk=s
                while 1:
                    tk+=d
                    if not(0<=tk<64)or abs(tk%8-((tk-d)%8))>1:break
                    if b[tk]==0:ms.append((s,tk,0,0));continue
                    if(b[tk]>0)!=w:ms.append((s,tk,0,0))
                    break
        elif t==5:
            for d in BD+RD:
                tk=s
                while 1:
                    tk+=d
                    if not(0<=tk<64)or abs(tk%8-((tk-d)%8))>1:break
                    if b[tk]==0:ms.append((s,tk,0,0));continue
                    if(b[tk]>0)!=w:ms.append((s,tk,0,0))
                    break
        elif t==6:
            for tk in KA[s]:
                if b[tk]==0 or(b[tk]>0)!=w:ms.append((s,tk,0,0))
            if w:
                if(cas&1)and b[61]==0 and b[62]==0 and b[63]==4:
                    if not atk(b,60,-1)and not atk(b,61,-1)and not atk(b,62,-1):ms.append((60,62,0,1))
                if(cas&2)and b[57]==0 and b[58]==0 and b[59]==0 and b[56]==4:
                    if not atk(b,60,-1)and not atk(b,59,-1)and not atk(b,58,-1):ms.append((60,58,0,2))
            else:
                if(cas&4)and b[5]==0 and b[6]==0 and b[7]==-4:
                    if not atk(b,4,1)and not atk(b,5,1)and not atk(b,6,1):ms.append((4,6,0,1))
                if(cas&8)and b[1]==0 and b[2]==0 and b[3]==0 and b[0]==-4:
                    if not atk(b,4,1)and not atk(b,3,1)and not atk(b,2,1):ms.append((4,2,0,2))
    return ms

def do_move(b,m,side,ep):
    f,t,pr,cf=m
    nb=list(b)
    nb[f]=0
    nep=-1
    if pr:
        nb[t]=pr
    else:
        nb[t]=b[f]
        if abs(b[f])==1 and t==ep:
            nb[t+(8 if side==-1 else-8)]=0
        if abs(b[f])==1 and abs(f-t)==16:
            nep=(f+t)//2
        if cf==1:
            if side==1:nb[63]=0;nb[61]=4
            else:nb[7]=0;nb[5]=-4
        elif cf==2:
            if side==1:nb[56]=0;nb[59]=4
            else:nb[0]=0;nb[3]=-4
    return nb,nep

def do_move_fast(b,m,side,ep):
    f,t,pr,cf=m
    nb=b[:]
    nb[f]=0
    nep=-1
    if pr:
        nb[t]=pr
    else:
        nb[t]=b[f]
        if abs(b[f])==1 and t==ep:
            nb[t+(8 if side==-1 else-8)]=0
        if abs(b[f])==1 and abs(f-t)==16:
            nep=(f+t)//2
        if cf==1:
            if side==1:nb[63]=0;nb[61]=4
            else:nb[7]=0;nb[5]=-4
        elif cf==2:
            if side==1:nb[56]=0;nb[59]=4
            else:nb[0]=0;nb[3]=-4
    return nb,nep

def upd_cas(cas,f,t):
    c=cas
    if f==60 or t==60:c&=~3
    if f==4 or t==4:c&=~12
    if f==63 or t==63:c&=~1
    if f==56 or t==56:c&=~2
    if f==7 or t==7:c&=~4
    if f==0 or t==0:c&=~8
    return c

def legal_moves(b,cas,ep,side):
    ksq=find_king(b,side)
    ms=gen_moves(b,cas,ep,side)
    leg=[]
    opp=-side
    for m in ms:
        f,t=m[0],m[1]
        nb,nep=do_move(b,m,side,ep)
        k=ksq if abs(b[f])!=6 else t
        if not atk(nb,k,opp):leg.append(m)
    return leg

def uci(m):
    f,t,pr,cf=m
    fn={2:"n",3:"b",4:"r",5:"q"}
    s=chr(f%8+97)+str(8-f//8)+chr(t%8+97)+str(8-t//8)
    if pr:s+=fn.get(abs(pr),"")
    return s

# Node counter
ns=0

def search(b,cas,ep,side,a,bt,d):
    global ns
    ns+=1
    if d==0:return quiesce(b,side,a,bt)
    ksq=find_king(b,side)
    opp=-side
    ms=gen_moves(b,cas,ep,side)
    leg=[]
    for m in ms:
        f,t=m[0],m[1]
        nb,nep=do_move_fast(b,m,side,ep)
        k=ksq if abs(b[f])!=6 else t
        if not atk(nb,k,opp):leg.append(m)
    if not leg:
        if atk(b,ksq,opp):return-99999
        return 0
    leg.sort(key=lambda m:V[abs(b[m[1]])]*10-V[abs(b[m[0]])] if b[m[1]]!=0 else 0,reverse=1)
    best=-99999
    for m in leg:
        nb,nep=do_move_fast(b,m,side,ep)
        nc=upd_cas(cas,m[0],m[1])
        v=-search(nb,nc,nep,opp,-bt,-a,d-1)
        if v>best:best=v
        if v>a:a=v
        if a>=bt:break
    return best

def quiesce(b,side,a,bt):
    global ns
    ns+=1
    stand=ev(b)*side
    if stand>=bt:return bt
    if stand>a:a=stand
    ksq=find_king(b,side)
    opp=-side
    ms=gen_moves(b,0,-1,side)
    caps=[]
    for m in ms:
        f,t=m[0],m[1]
        if b[t]!=0 or m[2]!=0:
            nb,_=do_move_fast(b,m,side,-1)
            k=ksq if abs(b[f])!=6 else t
            if not atk(nb,k,opp):caps.append(m)
    caps.sort(key=lambda m:V[abs(b[m[1]])]*10-V[abs(b[m[0]])] if b[m[1]]!=0 else 0,reverse=1)
    for m in caps:
        nb,_=do_move_fast(b,m,side,-1)
        v=-quiesce(nb,opp,-bt,-a)
        if v>a:a=v
        if a>=bt:break
    return a

def best_move(b,cas,ep,side,depth):
    global ns
    ksq=find_king(b,side)
    opp=-side
    ms=gen_moves(b,cas,ep,side)
    leg=[]
    for m in ms:
        f,t=m[0],m[1]
        nb,nep=do_move_fast(b,m,side,ep)
        k=ksq if abs(b[f])!=6 else t
        if not atk(nb,k,opp):leg.append(m)
    if not leg:return None
    # Iterative deepening with node budget
    NODE_BUDGET=15000
    bm=leg[0];ba=-99999
    d=1
    while d<=depth:
        ns0=ns
        leg.sort(key=lambda m:V[abs(b[m[1]])]*10-V[abs(b[m[0]])] if b[m[1]]!=0 else 0,reverse=1)
        ok=1
        for m in leg:
            nb,nep=do_move_fast(b,m,side,ep)
            nc=upd_cas(cas,m[0],m[1])
            v=-search(nb,nc,nep,opp,-99999,99999,d-1)
            if v>ba:ba=v;bm=m
            if ns-ns0>NODE_BUDGET:ok=0;break
        if not ok:break
        d+=1
    return uci(bm) if bm else None

def parse_fen(f):
    b=[0]*64;r=f.split();bs=r[0];side=1 if r[1]=="w" else-1;cas=0
    if"K"in r[2]:cas|=1
    if"Q"in r[2]:cas|=2
    if"k"in r[2]:cas|=4
    if"q"in r[2]:cas|=8
    ep=-1
    if r[3]!="-":ep=(8-(ord(r[3][1])-48))*8+(ord(r[3][0])-97)
    sq=0
    for c in bs:
        if c=="/":continue
        if c.isdigit():sq+=int(c);continue
        b[sq]=PM[c];sq+=1
    return b,cas,ep,side

def post(path,body):
    try:
        req=urllib.request.Request(ENV+path,data=json.dumps(body).encode(),headers={"content-type":"application/json"})
        with urllib.request.urlopen(req)as res:return json.load(res)
    except urllib.error.HTTPError as e:sys.exit(f"{path}: HTTP {e.code}")

def main():
    if not ENV:sys.exit(0)
    DEPTH=3
    while True:
        g=post("/game",{})
        if g["status"]=="done":break
        while g["status"]=="your_move":
            b,cas,ep,side=parse_fen(g["fen"])
            m=best_move(b,cas,ep,side,DEPTH)
            if m is None:
                m=g["legal_moves"][0]
            g=post("/move",{"game":g["game"],"move":m})
        print(f"game {g['game']}: {g['outcome']} by {g.get('reason','')}",file=sys.stderr)
    print(f"done: {g.get('wins')}W {g.get('draws')}D {g.get('losses')}L",file=sys.stderr)

if __name__=="__main__":main()
