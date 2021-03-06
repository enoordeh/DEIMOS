c-----------------------------------------------------------------------
      subroutine iylm(thmin,thmax,w,lmax1,nw,v)
      integer lmax1,nw
      real*8 thmin,thmax,w(nw)
c        work array (could be automatic if compiler supports it)
      real*8 v(lmax1)
c
c        parameters
      include 'pi.par'
c        data variables
      real*8 tiny
c        local (automatic) variables
      integer lm,lmx1,qphi
      real*8 ri,phi,zi,ci,si,ph,dph
c *
c * w_lm = integral from thmin to thmax Y_lm(th,0) sin th d th
c *
c * ISN'T THERE A FASTER WAY OF DOING THIS?
c * I can find an expansion in incomplete beta functions,
c * but the expansion is not much shorter, and not as pretty.
c *
c  Input: thmin, thmax = minimum, maximum polar angle in radians.
c         lmax1 = lmax+1 where lmax is maximum desired l of transform.
c         nw = [(lmax+1)*(lmax+2)]/2 .
c Output: w(lm) = integral from thmax to thmin Y_lm(th,0) d cos th .
c Work array: v should be dimensioned at least lmax1 .
c
      data tiny /1.d-30/
c
      do 120 lm=1,nw
        w(lm)=0.d0
  120 continue
c        upper latitude term
      ri=0.d0
      zi=1.d0
      phi=0.d0
      ph=0.d0
      dph=-tiny
      if (thmin.eq.0.d0.or.thmin.eq.PI) then
        si=0.d0
        lmx1=1
      else
        si=sin(thmin)
        lmx1=lmax1
      endif
      ci=cos(thmin)
      call wlm(w,lmx1,1,nw,ri,phi,0,zi,ci,si,ph,dph,v)
c        lower latitude term
      dph=tiny
      if (thmax.eq.0.d0.or.thmax.eq.PI) then
        si=0.d0
        lmx1=1
      else
        si=sin(thmax)
        lmx1=lmax1
      endif
      ci=cos(thmax)
      call wlm(w,lmx1,1,nw,ri,phi,0,zi,ci,si,ph,dph,v)
c        longitude term
      ri=1.d0
      zi=0.d0
      ci=0.d0
      si=1.d0
      phi=tiny
      qphi=-1
      ph=PI-(thmin+thmax)/2.d0
      dph=thmax-thmin
      call wlm(w,lmax1,1,nw,ri,phi,qphi,zi,ci,si,ph,dph,v)
      do 140 lm=1,nw
        w(lm)=w(lm)/tiny
  140 continue
      return
      end
c
