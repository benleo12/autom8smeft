import sys, re, itertools
import numpy as np
sys.path.insert(0,'${DIM8_ROOT:-.}/validate')
import zero_lorentz as Z

G=Z.G; EPS=Z.EPS
UFO='${DIM8_ROOT:-.}/models/dim8_is'
L=open(UFO+'/lorentz.py').read()
def struct(n):
    return re.search(rf"{n} = Lorentz\(.*?structure = '([^']*)'",L,re.S).group(1)

# deterministic kinematics: 4 incoming momenta summing to zero, generic (off-shell ok, the
# vertex is a polynomial identity so any momenta work)
rng=np.random.default_rng(7)
p={i:rng.normal(size=4) for i in (1,2,3)}
p[4]=-(p[1]+p[2]+p[3])
e={i:rng.normal(size=4) for i in (1,2,3,4)}

def ev(name):
    """evaluate a UFO Lorentz string with free index i contracted with e[i] (upper)."""
    parsed=Z.parse(struct(name)); assert parsed is not None, name
    total=0.0
    for sign,coef,named in parsed:
        tensors=[(EPS if n=='Epsilon' else G if n=='Metric' else G@p[a[1]], a if n!='P' else [a[0]]) for n,a in named]
        labels={}; letters=iter('abcdefghijklmnopqrstuvwxyz'); specs=[]; arrays=[]
        for arr,idx in tensors:
            s=''
            for i in idx:
                if i not in labels: labels[i]=next(letters)
                s+=labels[i]
            specs.append(s); arrays.append(arr)
        for i,l in list(labels.items()):
            if i>0: specs.append(l); arrays.append(e[i])
        for i in [k for k in labels if k<0]:
            l=labels[i]; l2=next(letters); seen=False; new=[]
            for sp in specs:
                if l in sp and not seen and sp.count(l)==1: seen=True; new.append(sp); continue
                if l in sp and seen: sp=sp.replace(l,l2,1)
                new.append(sp)
            specs=new; specs.append(l+l2); arrays.append(G)
        total+=sign*coef*np.einsum(','.join(specs)+'->',*arrays,optimize=True)
    return total

# field strengths for each leg, LOWER indices: f_{mu nu} = p_mu e_nu - p_nu e_mu
f={i: np.einsum('m,n->mn',G@p[i],G@e[i]) - np.einsum('m,n->mn',G@e[i],G@p[i]) for i in (1,2,3,4)}
def dot(a,b):            # a_{mn} b^{mn}
    return np.einsum('mn,mn->',a,G@b@G)
def dual(a):             # atilde_{mn} = 1/2 eps_{mnrs} a^{rs}
    return 0.5*np.einsum('mnrs,rs->mn',EPS,G@a@G)

pairings=[((1,2),(3,4)),((1,3),(2,4)),((1,4),(2,3))]
S1=sum(dot(f[i],f[j])*dot(f[k],f[l]) for (i,j),(k,l) in pairings)          # (B.B)^2
S2=sum(dot(f[i],dual(f[j]))*dot(f[k],dual(f[l])) for (i,j),(k,l) in pairings)  # (B.Btil)^2

v139=ev('VVVV139'); v28=ev('VVVV28')
print("hand  (B.B)^2   vertex/(8 i c) =", S1)
print("UFO   32*VVVV139               =", 32*v139, "   ratio =", 32*v139/S1)
print("hand  (B.Btil)^2 vertex/(8 i c)=", S2)
print("UFO    8*VVVV28                =",  8*v28,  "   ratio =",  8*v28/S2)
# the FT9 = Tr(B^4) prediction, as the vertex it would produce
# Tr form:  B_{a m} B^{m}{}_{b} B^{b}{}_{n} B^{n a}  -> per-leg permutation sum
def trterm(perm):
    a,b,c,d=[f[i]@G for i in perm]
    return np.trace(a@b@c@d)
Str=sum(trterm(pm) for pm in itertools.permutations((1,2,3,4)))
print("hand  Tr(B^4)   vertex/(i c)   =", Str)
print("pred  (1/2)*8*S1 + (1/4)*8*S2  =", 0.5*8*S1+0.25*8*S2, "  diff =", Str-(4*S1+2*S2))
