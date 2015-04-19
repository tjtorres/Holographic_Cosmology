import numpy as np
import scipy as sp
from scipy import integrate

conversion = 3.08e22*1e-17/(2.99e8)

class FuncTupple:
    def __init__(self, timeArray, funcArray, index):
        self.time = timeArray
        self.func = funcArray
        self.index = index



class Inflate:
    
    def __init__(self, t, b,c,w,R,t0,start, end):
        self.t = t
        self.b = b
        self.c = c
        self.w = w
        self.R = R
        self.t0 = t0
        self.a = self.scale(self.t)#/self.scale(self.t[0])
        self.adot = self.deriv(self.t,self.a)
        self.addot = self.deriv(self.t,self.adot)
        self.H = self.adot/self.a
        self.Hdot = self.deriv(self.t,self.H)
        self.pos = self.positive(self.t,self.addot)
        self.start= start
        self.end=end
        
    def T(self,t,b):
        return (1/2.)*(1. + np.tanh(t/b))
    
    def scale(self,t):
        #t=self.t
        b1=self.b
        c1=self.c
        w1=self.w
        R1=self.R
        t01=self.t0
        return c1*(np.sinh(t/R1)**(1./3.))*self.T(t01-t,b1) + t**((2./3.)*(1+w1))*self.T(t-t01,b1)
    
    def deriv(self,t,func):
        dx = t[1]-t[0]
        df = np.gradient(func,dx, edge_order=2)
        df[0]=2.*df[1]-df[2]
        return df
    
    def confTime(self):
        return sp.integrate.cumtrapz(1/self.a,self.t,initial=0)
    
    def apparentHor(self):
        return .5*self.confTime()*self.scale(self.confTime()/2.)
    
    def positive(self,t,array):
        
        compact=[]
        ind=0
#         for i in range(array.shape[0]-1):
#             if np.sign(array[i])==1 and np.sign(array[i+1])==-1:
                
#                 ind=i
#                 break
        index = [i for i,x in enumerate(array) if x>=0 ]#and i<= ind]
        
        function = FuncTupple(t[index],array[index],index)
        return function

    def  efolds(self):
        cl = self.pos
        
        if not cl.index:
            return 0.
        else: 
            astart = self.a[cl.index[0]]
            aend = self.a[cl.index[-1]]
            return np.log(aend/astart)
    
    def correlator(self,deltaS):
        H= self.H
        Hdot = self.Hdot
        k = self.adot
        return 9.*(H/Hdot)**2. *(np.exp(self.t/self.R)**(-4.*deltaS))*k**(2.*deltaS)

    def nsminus1(self,deltaS):
        answer =(self.adot*self.deriv(self.t,np.log(self.correlator(deltaS)))/self.addot)
        return answer[self.pos.index]
    def logk(self):
        return np.log(self.adot*(conversion))[self.pos.index]
    
    def check_Hdot_neg(self):
        
        return all(self.Hdot[3:]<0)
    
    def nsm1_val(self, target=.9603-1):
        start=self.start
        end=self.end
        x = np.linspace(0.0,1.5,30)
        y = self.logk()[start:end]
        ns = np.zeros((x.shape[0], y.shape[0]))
        try:
            for i,dS in enumerate(x):
                ns[i] = self.nsminus1(dS)[start:end]
        
            q=[]
            for i in range(x.shape[0]):
                q.append( sp.interpolate.interp1d(y,ns[i]))
        
   
            interp = np.asarray([[(q[i](np.log(.002)))[()],x1] for i,x1 in enumerate(x)])

            nsm1 = sp.interpolate.interp1d(interp[:,0], interp[:,1])
            return nsm1(target)[()]
    
        except ValueError:
            return None
        
    def run(self):
        start=self.start
        end=self.end
        dS = self.nsm1_val()
        try:
            val = self.deriv(self.logk()[start:end], self.nsminus1(dS)[start:end])
        except TypeError:
            return None
        running = sp.interpolate.interp1d(self.logk()[start:end], val)

        try:
            return running(np.log(.038))
        except ValueError:
            return None