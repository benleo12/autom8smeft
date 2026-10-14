# Convention ledger

Every convention that can flip a sign or a factor of two between the Murphy basis
(arXiv:2005.00059) and the model, with the evidence and the test that pins it down.  A row is "closed"
only when a numerical test in this directory passes.

| Object | Murphy | FeynRules / UFO | Relation used in the encoding | Status |
|---|---|---|---|---|
| SU(2) generators | tau^I Pauli, t^I = tau/2 | `Ta[a,i,j]` = sigma/2 (PauliSigma/2 in M$GaugeGroups) | tau^I -> `2 Ta` | closed by construction |
| SU(3) generators | T^A = lambda/2 | `T[a,i,j]` = lambda/2 | T^A -> `T` | closed |
| d^{ABC} | d^{ABC} with {T^A,T^B} = delta/3 + d T | `dSUN[a,b,c]` (SymmetricTensor in M$GaugeGroups) | d -> `dSUN` | open: validate/check_colour_norm.wls checks {T^A,T^B} = delta/3 + d T on the numeric d^{ABC} of the vertex worker, not on FeynRules' `dSUN` itself |
| eps_{jk} | eps_{12} = +1 | `Eps[i,j]` = Signature -> Eps[1,2] = +1 | identity | closed |
| eps^{IJK} | standard | `Eps[a,b,c]` | identity | closed |
| H-tilde | H-tilde_j = eps_{jk} H^{dagger k} | `Eps[jj,kk] Phibar[kk]` | expanded | closed |
| Covariant derivative | D = d + i g A | FeynRules builds `DC` as d - i FR$DSign g A, and the base sets `FR$DSign = -1`, so D = d + i g A (FS and DC follow) | identity. The SM Lagrangian is built with the same D, so no relative sign enters | closed by construction (`FR$DSign = -1` in tests/gen_smoke/base.fr and base_inputscheme.fr; SMEFTsim sets the same value) |
| Levi-Civita, Lorentz | eps_{0123} = +1 (so eps^{0123} = -1) | FR: `Eps[mu,nu,rho,sig]` numeric = Signature. Passed to UFO as `Epsilon(1,2,3,4)` unchanged (PYSplitStructures.m:16). ALOHA `L_Epsilon.give_parity((0,1,2,3)) = -1` (aloha_object.py:949), i.e. Epsilon components with contravariant index placement have eps^{0123} = -1, equivalently eps_{0123} = +1 | `epsLorSign = +1` | open: no numerical test in this directory fixes the sign. The SmeftFR comparison writes the dual the same way on both sides, so the sign cancels there, and operators with two duals do not depend on it |
| sigma^{mu nu} | i/2 [gamma^mu, gamma^nu] | `Sig[mu,nu,s1,s2]` = I/2 (Ga.Ga - Ga.Ga) | identity | closed (FeynRules manual) |
| Hermitian derivative | i H^dag Dlr H = i H^dag D H - i (D H^dag) H | expanded in dsl.iHDlrH | identity | closed |
| Dual field strength | Xtilde_{mu nu} = 1/2 eps_{mu nu rho sigma} X^{rho sigma} | `(1/2) epsLorSign Eps[mu,nu,rho,sig] FS[X,rho,sig]` | identity up to epsLorSign | follows the Levi-Civita row |
| Charge conjugation | psi C psi = psi^T C psi | FeynRules `CC[psi]` | not used: only the baryon-number-violating classes need it, and they are not exported | not needed for the released models |
| Fermion chirality | l,q left; e,u,d right | `LL, QL` (ProjM), `lR, uR, dR` (ProjP) | identity | closed |
| Flavour | weak eigenstates, Yukawas general | Cabibbo-only CKM, diagonal option | universal mode identifies p=r per bilinear | closed for universal; open for general, which the released models do not use |
| Wilson coefficient normalisation | L = sum C Q with C of dimension -4 | `c/Lam^4` with Lam external (GeV) and c dimensionless | c = C Lam^4 | closed |
