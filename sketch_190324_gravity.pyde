fc = 2
wd = 1080/fc; ht = 1080/fc

G = 200
tstep = 1e-3
dmag = 1
fpstep = 50
fskip = 1
ns = 5
glim = PVector(.85,1)
clim = PVector(-.5,.5)

def settings():
    size(wd,ht)

def setup():
    global ps,p1,bg
    colorMode(HSB,1.)
    background(0)
    ellipseMode(RADIUS)
    noFill()
    ###
    p1 = particle(PVector(width/2,height/2),PVector(20,20),
                  3,10,color(.65,1,1),False)
    pg1 = particle(PVector(width/4,height/2),PVector(0,0),
                  30,1000,color(0,0,1),True)
    pg2 = particle(PVector(width/4*3,height/2),PVector(0,0),
                  30,1000,color(0,0,1),True)
    pg3 = particle(PVector(width/2,height/4),PVector(0,0),
                  30,1000,color(0,0,1),True)
    pg8 = particle(PVector(width/2,height/4*3),PVector(0,0),
                  30,1000,color(0,0,1),True)
    pg4 = particle(PVector(width,height),PVector(0,0),
                  10,-15000,color(0,0,1),True)
    pg5 = particle(PVector(0,height),PVector(0,0),
                  10,-15000,color(0,0,1),True)
    pg6 = particle(PVector(width,0),PVector(0,0),
                  10,-15000,color(0,0,1),True)
    pg7 = particle(PVector(0,0),PVector(0,0),
                  10,-15000,color(0,0,1),True)    
    ps = [pg1,pg2,pg3,pg8]
    nvec = 76
    rvec = 1.*width/nvec
    bg = createGraphics(width,height)
    bg.beginDraw()
    bg.colorMode(HSB,1.)
    bg.ellipseMode(RADIUS)
    for i in xrange(nvec):
        x = map(i,0,nvec,0,width)
        for j in xrange(nvec):
            y = map(j,0,nvec,0,height)
            pos = PVector(x+rvec/2.,y+rvec/2.)
            pvec = PVector(0,0)
            h = 0
            for m in xrange(len(ps)):
                pdif = PVector.sub(ps[m].pos,pos)
                theta = pdif.heading()
                nse = noise(cos(theta*3)*ns)
                gvar = map(nse,0,.8,glim.x,glim.y)
                fvec = gvar*G*ps[m].M/(pdif.magSq()*dmag*dmag+1e6)
                pdif.setMag(fvec)
                pvec.add(pdif)
                h += map(pdif.mag(),ps[m].R,width/4.,clim.x,clim.y)
            pvec.setMag(rvec*4)
            bg.stroke(hloop(h),1,.2)
            bg.line(pos.x,pos.y,pos.x+pvec.x,pos.y+pvec.y)
    for i in ps:
        bg.stroke(i.col)
        bg.fill(0)
        bg.ellipse(i.pos.x,i.pos.y,i.R,i.R)
    bg.endDraw()
    
    for i in ps: i.show()

def draw():
    background(0)
    image(bg,0,0)
    for i in xrange(fpstep):
        p1.addF(ps)
        p1.update()
        p1.oob(ps)
    if frameCount%fskip == 0: p1.show()

###########

class particle():
    def __init__(self,pos,vel,R,M,col,fix):
        self.pos = pos
        self.vel = vel
        self.acc = PVector(0,0)
        self.R = R
        self.M = M
        self.col = col
        self.fix = fix
    
    def show(self):
        stroke(self.col)
        fill(0)
        ellipse(self.pos.x,self.pos.y,self.R,self.R)
        # v = PVector.fromAngle(self.vel.heading())
        # v.setMag(30)
        # stroke(.35,1,1)
        # line(self.pos.x,self.pos.y,
        #      self.pos.x+v.x,self.pos.y+v.y)
    
    def addF(self,pL):
        hnew = 0
        for i in xrange(len(pL)):
            pdif = PVector.sub(pL[i].pos,self.pos)
            theta = pdif.heading()
            nse = noise(cos(theta*3)*ns)
            gvar = map(nse,0,.8,glim.x,glim.y)
            hc = map(pdif.mag(),pL[i].R,width/2.,clim.x,clim.y)
            hnew += map(nse,0,.8,0,1)*0 + hc
            F = gvar*G*pL[i].M/(pdif.magSq()*dmag*dmag)
            Fv = PVector(F*cos(theta),F*sin(theta))
            self.acc.add(Fv)
        hp = map(self.vel.heading(),-PI,PI,-.1,.1)
        self.col = color(hloop(hnew+hp),1,1)
    
    def update(self):
        if not(self.fix):
            self.vel.add(PVector.mult(self.acc,tstep))
            self.pos.add(PVector.mult(self.vel,tstep))
        self.acc.mult(0)
    
    def oob(self,pL):
        for i in xrange(len(pL)):
            pdif = PVector.sub(pL[i].pos,self.pos)
            rdif = pL[i].R + self.R
            if pdif.mag() < rdif:
                pdif.mult(-1)
                I = PVector.fromAngle(self.vel.heading())
                N = PVector.fromAngle(pdif.heading())
                
                abdot = PVector.dot(N,I)
                a2d = PVector.mult(N,2*abdot)
                nvel = PVector.sub(I,a2d)
                nvel.setMag(self.vel.mag())
                self.vel = nvel.copy()
                self.update()

####

def hloop(h):
    return h - floor(h)
