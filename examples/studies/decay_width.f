      PROGRAM DECAY_WIDTH
C     The partial width of a two-body decay from MadGraph's standalone matrix element, which
C     run_study.sh compiles in place of check_sa.f for a process with one particle in.
C     The matrix element summed over the helicities of the products and averaged over those of
C     the decaying particle does not depend on the direction of the decay, so the width is
C         Gamma = |M|^2 |p| / (8 pi M^2)
C     with M the mass of the decaying particle and |p| the momentum of either product in its rest
C     frame (MadGraph's matrix element already divides by the symmetry factor of identical
C     products).  The matrix element is evaluated along three directions and printed for each, and
C     examples/studies/provenance.py checks that the three agree and that the width is the one
C     they give.
C     The integration of bin/generate_events is not used for a decay.  MadEvent gives a
C     phase-space point the weight +-sum_h |M_h|^2, the sign that of a helicity h drawn with
C     probability |M_h|^2 / sum_h |M_h|^2, and takes its error from the absolute values of the
C     weights.  In a two-body decay the absolute value is the same at every point, so the error
C     it quotes is 1e-8 of the width whatever the draws gave.  The 1/Lambda^2 term of
C     z > e+ e-, whose helicities enter with both signs, came out 25 per cent high in the
C     survey with that error.
      IMPLICIT NONE
C     pmass.inc writes a massless particle's mass as ZERO, as check_sa.f does
      REAL*8 ZERO
      PARAMETER (ZERO=0D0)
      INCLUDE "coupl.inc"
      INCLUDE "nexternal.inc"
      REAL*8 PMASS(NEXTERNAL), P(0:3,NEXTERNAL)
      REAL*8 ME(3), DIRS(2,3), PI, KL, PABS, CT, ST
      INTEGER I, K
C     cos(theta) and phi of the three directions
      DATA DIRS /0.3D0, 0.7D0,  -0.8D0, 2.1D0,  0.95D0, 4.4D0/

      PI = 4D0*DATAN(1D0)
      CALL SETPARA('../../Cards/param_card.dat')
      INCLUDE "pmass.inc"
      IF (NINCOMING.NE.1 .OR. NEXTERNAL.NE.3) THEN
        WRITE(*,*) 'decay_width: not a two-body decay'
        STOP 1
      ENDIF
      KL = (PMASS(1)**2-(PMASS(2)+PMASS(3))**2)
     $   * (PMASS(1)**2-(PMASS(2)-PMASS(3))**2)
      IF (KL.LE.0D0) THEN
        WRITE(*,*) 'decay_width: the decay is closed'
        STOP 1
      ENDIF
      PABS = DSQRT(KL)/(2D0*PMASS(1))
      DO K = 1, 3
        CT = DIRS(1,K)
        ST = DSQRT(1D0-CT**2)
        P(0,1) = PMASS(1)
        P(1,1) = 0D0
        P(2,1) = 0D0
        P(3,1) = 0D0
        P(0,2) = DSQRT(PABS**2+PMASS(2)**2)
        P(1,2) = PABS*ST*DCOS(DIRS(2,K))
        P(2,2) = PABS*ST*DSIN(DIRS(2,K))
        P(3,2) = PABS*CT
        P(0,3) = DSQRT(PABS**2+PMASS(3)**2)
        DO I = 1, 3
          P(I,3) = -P(I,2)
        ENDDO
        CALL SMATRIX(P, ME(K))
      ENDDO
      WRITE(*,'(A,ES24.16)') ' mass of the decaying particle (GeV) = ',
     $  PMASS(1)
      WRITE(*,'(A,2ES24.16)') ' masses of the products (GeV) = ',
     $  PMASS(2), PMASS(3)
      WRITE(*,'(A,ES24.16)') ' momentum of a product (GeV) = ', PABS
      DO K = 1, 3
        WRITE(*,'(A,I1,A,3ES24.16)') ' matrix element ', K,
     $    ' (GeV^2, cos theta, phi) = ', ME(K), DIRS(1,K), DIRS(2,K)
      ENDDO
      WRITE(*,'(A,ES24.16)') ' width (GeV) = ',
     $  ME(1)*PABS/(8D0*PI*PMASS(1)**2)
      END
