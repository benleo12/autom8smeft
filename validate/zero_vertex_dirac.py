#!/usr/bin/env python3
"""Numeric vertex-level zero test with Dirac structures.

Evaluates  sum_{i,j} C_{ij} Color_i Lorentz_j  for every vertex whose coupling set touches a
given Wilson coefficient, at random momenta, as an explicit tensor in the external spinor and
Lorentz indices.  Reports max|component| relative to the max over individual terms.
"""
import re, sys, itertools
import numpy as np

UFO = sys.argv[1] if len(sys.argv) > 1 else '${DIM8_ROOT:-.}/models/dim8_is'
WCPAT = sys.argv[2] if len(sys.argv) > 2 else r'c8(e|l|q|u|d)4B'

G = np.diag([1.,-1,-1,-1])
EPS = np.zeros((4,4,4,4))
for p in itertools.permutations(range(4)):
    s=1; q=list(p)
    for i in range(4):
        for j in range(i+1,4):
            if q[i]>q[j]: s=-s
    EPS[p]=s
# Dirac matrices, Weyl basis, gamma^mu with UPPER index
I2=np.eye(2); sx=np.array([[0,1],[1,0]],complex); sy=np.array([[0,-1j],[1j,0]]); sz=np.diag([1,-1]).astype(complex)
sig=[I2,sx,sy,sz]; sigb=[I2,-sx,-sy,-sz]
GA=[np.block([[np.zeros((2,2)),sig[m]],[sigb[m],np.zeros((2,2))]]) for m in range(4)]
G5=1j*GA[0]@GA[1]@GA[2]@GA[3]
PR=(np.eye(4)+G5)/2; PL=(np.eye(4)-G5)/2
ID4=np.eye(4,dtype=complex)

L=open(UFO+'/lorentz.py').read(); V=open(UFO+'/vertices.py').read(); C=open(UFO+'/couplings.py').read()
LOR=dict(re.findall(r"(\w+) = Lorentz\(name = '\w+',\s*spins = \[[^\]]*\],\s*structure = '([^']*)'",L))
COUP=dict((n,v) for n,v in re.findall(r"(GC_\d+) = Coupling\(name = '\w+',\s*value = '([^']*)'",C))

def split_top(s, ch):
    out,d,cur=[],0,''
    for c in s:
        if c=='(': d+=1
        if c==')': d-=1
        if c==ch and d==0: out.append(cur); cur=''
        else: cur+=c
    out.append(cur); return out

def terms(struct):
    """[(sign, coeff, [(name,args)])]"""
    s=struct.replace(' ',''); out=[]; d=0; cur=''; sign=1
    for c in s:
        if c=='(': d+=1
        if c==')': d-=1
        if c in '+-' and d==0:
            if cur: out.append((sign,cur)); cur=''
            sign = 1 if c=='+' else -1
            if not cur and c=='-' and not out and not cur: pass
        else: cur+=c
    if cur: out.append((sign,cur))
    res=[]
    for sg,t in out:
        while t.startswith('(') and t.endswith(')') and min(np.cumsum([1 if c=='(' else -1 if c==')' else 0 for c in t[:-1]]))>0:
            t=t[1:-1]
        coef=1.0; tens=[]
        for f in split_top(t,'*'):
            while f.startswith('(') and f.endswith(')'):
                inner=f[1:-1]
                if min(np.cumsum([1 if c=='(' else -1 if c==')' else 0 for c in inner]+[1]))<0: break
                f=inner
            m=re.match(r'(Epsilon|P|Metric|Identity|Gamma5|Gamma|ProjP|ProjM|Sigma)\(([^()]*)\)$',f)
            if m: tens.append((m.group(1),[int(a) for a in m.group(2).split(',')] if m.group(2) else []))
            else: coef*=complex(eval(f,{'__builtins__':{}},{'complex':complex}))
        res.append((sg,coef,tens))
    return res

# slot types: 'L' lorentz index, 'S' spinor index, 'M' momentum leg label
SLOT={'Epsilon':'LLLL','P':'LM','Metric':'LL','Identity':'SS','Gamma':'LSS','Gamma5':'SS',
      'ProjP':'SS','ProjM':'SS','Sigma':'LLSS'}

def ev_lorentz(name, nferm, nvec, mom):
    """array indexed by [spinor legs..., vector legs...] (all 4-dim)."""
    st=LOR[name]
    ferm=list(range(1,nferm+1)); vec=list(range(nferm+1,nferm+nvec+1))
    shape=tuple([4]*nferm+[4]*nvec)
    tot=np.zeros(shape,complex); scale=0.0
    for sg,coef,tens in terms(st):
        specs=[]; arrs=[]; lab={}; letters=iter('abcdefghijklmnopqrstuvwxyzABCDEFGHIJ')
        def L_(i):
            key=('L',i)
            if key not in lab: lab[key]=next(letters)
            return lab[key]
        def S_(i):
            key=('S',i)
            if key not in lab: lab[key]=next(letters)
            return lab[key]
        raise_pairs=[]
        for nm,args in tens:
            slots=SLOT[nm]
            if nm=='P':
                specs.append(L_(args[0])); arrs.append(G@mom[args[1]])   # lower index
            elif nm=='Metric':
                specs.append(L_(args[0])+L_(args[1])); arrs.append(G)
            elif nm=='Epsilon':
                specs.append(''.join(L_(a) for a in args)); arrs.append(EPS)  # lower
            elif nm=='Identity':
                specs.append(S_(args[0])+S_(args[1])); arrs.append(ID4)
            elif nm=='ProjP':
                specs.append(S_(args[0])+S_(args[1])); arrs.append(PR)
            elif nm=='ProjM':
                specs.append(S_(args[0])+S_(args[1])); arrs.append(PL)
            elif nm=='Gamma5':
                specs.append(S_(args[0])+S_(args[1])); arrs.append(G5)
            elif nm=='Gamma':
                # gamma^mu upper -> lower with metric handled by the dummy-raise pass
                specs.append(L_(args[0])+S_(args[1])+S_(args[2]))
                arrs.append(np.einsum('mn,mij->nij',G,np.array(GA)))       # gamma_mu
            else:
                raise RuntimeError(nm)
        # raise every contracted pair (a lorentz or spinor label appearing twice) once
        allspec=''.join(specs)
        for (kind,idx),l in lab.items():
            if allspec.count(l)==2:
                if kind=='L':
                    l2=next(letters); seen=False; new=[]
                    for sp in specs:
                        if l in sp and not seen: seen=True; new.append(sp); continue
                        if l in sp: sp=sp.replace(l,l2,1)
                        new.append(sp)
                    specs=new; specs.append(l+l2); arrs.append(G)
        out=''.join(lab[('S',i)] for i in ferm)+''.join(lab[('L',i)] for i in vec)
        v=np.einsum(','.join(specs)+'->'+out,*arrs,optimize=True)
        tot=tot+sg*coef*v; scale=max(scale,np.abs(sg*coef*v).max())
    return tot, scale

def cval(expr, wc):
    """numeric value of a coupling with the target WC set to 1 and every other symbol to a
    generic nonzero number (only vertices carrying wc are tested, so other WCs are set to 0)."""
    env={'complex':complex,'Lam':1000.0,'vev':246.0,'ee':0.31,'cw':0.88,'sw':0.47,'G':1.2,
         'complexconjugate':lambda z: np.conj(z),'MW':80.4,'MZ':91.2,'MH':125.,'cmath':__import__('cmath'),'math':__import__('math')}
    for m in set(re.findall(r'\bc8\w+',expr)): env[m]=0.0
    env[wc]=1.0
    class D(dict):
        def __missing__(self,k):
            import hashlib
            return 0.3+0.7*(int(hashlib.md5(k.encode()).hexdigest()[:4],16)/65535.)
    d=D(env)
    return complex(eval(expr,{'__builtins__':{}},d))

VB=re.findall(r"(V_\d+) = Vertex\(name = '\w+',\s*particles = \[([^\]]*)\],\s*color = \[([^\]]*)\],\s*lorentz = \[([^\]]*)\],\s*couplings = \{([^}]*)\}\)",V)
wcs=sorted({w for w in set(re.findall(r'\bc8\w+',C)) if re.match(WCPAT,w)})
print(f"{'wc':12s} {'vertices':>8s} {'max|V|':>12s} {'max term':>12s} {'ratio':>10s}")
for wc in wcs:
    gcs={g for g,v in COUP.items() if re.search(rf'\b{wc}\b',v)}
    worst=0.0; nv=0; det=[]
    for name,parts,colors,lors,cps in VB:
        if not any(f'C.{g}' in cps for g in gcs): continue
        nv+=1
        P=[p.strip().replace('P.','') for p in parts.split(',')]
        nferm=sum(1 for p in P if re.match(r'(e|mu|ta|ve|vm|vt|u|c|t|d|s|b)(__plus__|__minus__|__tilde__)?$',p))
        nvec=len(P)-nferm
        LN=[x.strip().replace('L.','') for x in lors.split(',')]
        NC=len(split_top(colors,','))
        mom={i:np.random.default_rng(11+i).normal(size=4) for i in range(1,len(P)+1)}
        mom[len(P)]=-sum(mom[i] for i in range(1,len(P)))
        acc=None; sc=0.0
        for m in re.finditer(r'\((\d+),(\d+)\):C\.(GC_\d+)',cps):
            ci,li,g=int(m.group(1)),int(m.group(2)),m.group(3)
            c=cval(COUP[g],wc)
            if c==0: continue
            arr,s=ev_lorentz(LN[li],nferm,nvec,mom)
            key=ci
            if acc is None: acc={}
            acc[key]=acc.get(key,0)+c*arr; sc=max(sc,abs(c)*s)
        if acc is None: continue
        mx=max(np.abs(a).max() for a in acc.values())
        worst=max(worst,mx/max(sc,1e-300)); det.append((name,mx,sc))
    if det:
        mx=max(d[1] for d in det); sc=max(d[2] for d in det)
        print(f"{wc:12s} {nv:8d} {mx:12.3e} {sc:12.3e} {worst:10.2e}")
    else:
        print(f"{wc:12s} {nv:8d} {'-':>12s} {'-':>12s} {'-':>10s}")
