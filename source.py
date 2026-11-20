"""tiny-chess-01 — engine with TT, killers, history, king safety, check ext, mate scoring."""
import json,os,sys,urllib.error,urllib.request
ENV=os.environ.get("MAKEFUN_ENV_URL")
V=[0,100,320,330,500,900,20000]
MA=99000
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
def mir(s):return((7-s//8)*8+s%8)
def ev(b):
    e=0;wb=0;bb=0
    for s in range(64):
        p=b[s]
        if p==0:continue
        a=abs(p)
        v=V[a]+PS[a][s if p>0 else mir(s)]
        if a==3:
            if p>0:wb+=1
            else:bb+=1
        e+=v if p>0 else-v
    if wb>=2:e+=50
    if bb>=2:e-=50
    for s in range(64):
        if b[s]==1:
            f=s%8;bl=0
            for r in range(0,s//8):
                if b[r*8+f]!=0 and b[r*8+f]<0:bl=1;break
            if not bl:
                for df in(-1,1):
                    nf=f+df
                    if 0<=nf<8:
                        for r in range(0,s//8):
                            if b[r*8+nf]!=0 and b[r*8+nf]<0:bl=1;break
                    if bl:break
                if not bl:e+=20+(s//8)*5
        elif b[s]==-1:
            f=s%8;bl=0
            for r in range(s//8+1,8):
                if b[r*8+f]!=0 and b[r*8+f]>0:bl=1;break
            if not bl:
                for df in(-1,1):
                    nf=f+df
                    if 0<=nf<8:
                        for r in range(s//8+1,8):
                            if b[r*8+nf]!=0 and b[r*8+nf]>0:bl=1;break
                    if bl:break
                if not bl:e-=20+((7-s//8))*5
    # King safety
    for sk,op in[(6,-1),(-6,1)]:
        for s in range(64):
            if b[s]==sk:
                kf=s%8;kr=s//8;ps=0
                for df in(-1,0,1):
                    nf=kf+df
                    if 0<=nf<8:
                        pr=kr+(1 if sk==6 else-1)
                        if 0<=pr<8 and b[pr*8+nf]==op:ps+=1
                        pr2=kr+(2 if sk==6 else-2)
                        if 0<=pr2<8 and b[pr2*8+nf]==op:ps+=1
                if ps<4:
                    pen=(4-ps)*15
                    if sk>0:e-=pen
                    else:e+=pen
                break
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
def fk(b,side):
    t=6 if side==1 else-6
    for s in range(64):
        if b[s]==t:return s
    return 0
def gm(b,cas,ep,side):
    ms=[];w=side==1
    for s in range(64):
        pc=b[s]
        if pc==0 or(pc>0)!=w:continue
        t=abs(pc)
        if t==1:
            d=-8 if w else 8;sr=s//8;tk=s+d
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
def dm(b,m,side,ep):
    f,t,pr,cf=m;nb=b[:];nb[f]=0;nep=-1
    if pr:nb[t]=pr
    else:
        nb[t]=b[f]
        if abs(b[f])==1 and t==ep:nb[t+(8 if side==-1 else-8)]=0
        if abs(b[f])==1 and abs(f-t)==16:nep=(f+t)//2
        if cf==1:
            if side==1:nb[63]=0;nb[61]=4
            else:nb[7]=0;nb[5]=-4
        elif cf==2:
            if side==1:nb[56]=0;nb[59]=4
            else:nb[0]=0;nb[3]=-4
    return nb,nep
def uc(cas,f,t):
    c=cas
    if f==60 or t==60:c&=~3
    if f==4 or t==4:c&=~12
    if f==63 or t==63:c&=~1
    if f==56 or t==56:c&=~2
    if f==7 or t==7:c&=~4
    if f==0 or t==0:c&=~8
    return c
TT={};TTM=200000
kl=[None]*32
hi=[[0]*64 for _ in range(64)]
ns=0
def pk(b,cas,ep,side):return(tuple(b),cas,ep,side)
def ptt(key,d,a,bt,pl):
    return(False,0,None)
def stt(key,d,fl,sc,bm,pl):
    pass
def ml(b,cas,ep,side):
    ks=fk(b,side);op=-side;ms=gm(b,cas,ep,side);lg=[]
    for m in ms:
        f,t=m[0],m[1];nb,nep=dm(b,m,side,ep);k=ks if abs(b[f])!=6 else t
        if not atk(nb,k,op):lg.append(m)
    return lg
def ordm(lg,b,tm,d):
    def mv(m):
        if b[m[1]]!=0:return V[abs(b[m[1]])]*10-V[abs(b[m[0]])]
        if m[2]!=0:return V[abs(m[2])]*10
        return 0
    sc=[];k1=kl[d][0] if kl[d] else None;k2=kl[d][1] if kl[d] else None
    for m in lg:
        if m==tm:sc.append((100000,m))
        elif b[m[1]]!=0 or m[2]!=0:sc.append((mv(m)+50000,m))
        elif m==k1:sc.append((40000,m))
        elif m==k2:sc.append((35000,m))
        else:sc.append((hi[m[0]][m[1]],m))
    sc.sort(key=lambda x:x[0],reverse=1)
    return[m for _,m in sc]
def iq(m,b):return b[m[1]]==0 and m[2]==0
def npm(b,side):
    for s in range(64):
        p=b[s]
        if p!=0 and(p>0)==(side==1)and abs(p)>1 and p!=6*side:return True
    return False
def sr(b,cas,ep,side,a,bt,d,pl):
    global ns;ns+=1
    ma=max(-MA+pl,-MA+1);mb=min(MA-pl,MA-1)
    if a>=mb or bt<=ma:
        a=max(a,ma);bt=min(bt,mb)
        if a>=bt:return(a+bt)//2
    key=pk(b,cas,ep,side)
    hit,ts,tm=ptt(key,d,a,bt,pl)
    if hit:return ts
    if d==0:
        v=qs(b,side,a,bt,pl);stt(key,0,0,v,None,pl);return v
    ks=fk(b,side);op=-side;ic=atk(b,ks,op)
    R=2
    if not ic and npm(b,side) and d>=R+1:
        v=-sr(b,cas,-1,op,-bt,-bt+1,d-R-1,pl+1)
        if v>=bt:return bt
    lg=ml(b,cas,ep,side)
    if not lg:
        if ic:
            sc=-MA+pl;stt(key,d,0,sc,None,pl);return sc
        stt(key,d,0,0,None,pl);return 0
    od=ordm(lg,b,tm,d);be=-MA;bm=od[0];fl=2
    for m in od:
        nb,nep=dm(b,m,side,ep);nc=uc(cas,m[0],m[1])
        v=-sr(nb,nc,nep,op,-bt,-a,d-1,pl+1)
        if v>be:be=v;bm=m
        if v>a:a=v
        if a>=bt:
            fl=1
            if iq(m,b):
                if kl[d] is None:kl[d]=[None,None]
                if m!=kl[d][0]:kl[d][1]=kl[d][0];kl[d][0]=m
                hi[m[0]][m[1]]+=d*d
            break
    if fl==2 and bm:stt(key,d,0,be,bm,pl)
    elif fl==1:stt(key,d,fl,be,bm,pl)
    return be
def qs(b,side,a,bt,pl):
    global ns;ns+=1
    st=ev(b)*side
    if st>=bt:return bt
    if st>a:a=st
    ks=fk(b,side);op=-side;ic=atk(b,ks,op)
    if ic:
        ms=gm(b,0,-1,side);lg=[]
        for m in ms:
            f,t=m[0],m[1];nb,_=dm(b,m,side,-1);k=ks if abs(b[f])!=6 else t
            if not atk(nb,k,op):lg.append(m)
        if not lg:return-MA+pl
        for m in lg:
            nb,_=dm(b,m,side,-1);v=-qs(nb,op,-bt,-a,pl+1)
            if v>a:a=v
            if a>=bt:break
        return a
    ms=gm(b,0,-1,side);cp=[]
    for m in ms:
        f,t=m[0],m[1]
        if b[t]!=0 or m[2]!=0:
            nb,_=dm(b,m,side,-1);k=ks if abs(b[f])!=6 else t
            if not atk(nb,k,op):cp.append(m)
    cp.sort(key=lambda m:V[abs(b[m[1]])]*10-V[abs(b[m[0]])] if b[m[1]]!=0 else V[abs(m[2])]*10,reverse=1)
    for m in cp:
        nb,_=dm(b,m,side,-1);v=-qs(nb,op,-bt,-a,pl+1)
        if v>a:a=v
        if a>=bt:break
    return a
def bm(b,cas,ep,side,depth):
    global ns
    lg=ml(b,cas,ep,side)
    if not lg:return None
    NB=80000;bm=lg[0];ba=-MA;d=1
    while d<=depth:
        ns0=ns;tm=None
        od=ordm(lg,b,tm,d);ok=1
        for m in od:
            nb,nep=dm(b,m,side,ep);nc=uc(cas,m[0],m[1])
            v=-sr(nb,nc,nep,-side,-MA,MA,d-1,1)
            if v>ba:ba=v;bm=m
            if ns-ns0>NB:ok=0;break
        if not ok:break
        d+=1
    return uc2(bm) if bm else None
def uc2(m):
    f,t,pr,cf=m;fn={2:"n",3:"b",4:"r",5:"q"}
    s=chr(f%8+97)+str(8-f//8)+chr(t%8+97)+str(8-t//8)
    if pr:s+=fn.get(abs(pr),"")
    return s
def pf(f):
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
def po(path,body):
    try:
        req=urllib.request.Request(ENV+path,data=json.dumps(body).encode(),headers={"content-type":"application/json"})
        with urllib.request.urlopen(req)as res:return json.load(res)
    except urllib.error.HTTPError as e:sys.exit(f"{path}: HTTP {e.code}")
def main():
    if not ENV:sys.exit(0)
    DP=3
    while True:
        g=po("/game",{})
        if g["status"]=="done":break
        while g["status"]=="your_move":
            b,cas,ep,side=pf(g["fen"])
            m=bm(b,cas,ep,side,DP)
            if m is None:m=g["legal_moves"][0]
            g=po("/move",{"game":g["game"],"move":m})
        print(f"game {g['game']}: {g['outcome']} by {g.get('reason','')}",file=sys.stderr)
    print(f"done: {g.get('wins')}W {g.get('draws')}D {g.get('losses')}L",file=sys.stderr)
if __name__=="__main__":main()
