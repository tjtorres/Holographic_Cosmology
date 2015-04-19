import numpy as np
import scipy as sp
from scipy import integrate
from scipy import interpolate
from csv import writer
from HSTmodule import Inflate
import sys
import os.path
import codecs
from multiprocessing import Pool, Value

def init(count):
     global counter
     counter = count

def calculate_inflation(params):
    b,c,w,R,t0 = params
    inf = Inflate(t,b,c,w,R,t0,10,-10)
    valid = False
    efolds = inf.efolds()
    dS = inf.nsm1_val()
    if dS == None:
        dS_std = None
    else:
        try:
            dS_std = inf.nsm1_val(0.9676-1)- dS
        except:
            print 
            dS_std = None
    
        
    run = inf.run()
    
    #constraints
    if inf.check_Hdot_neg() and (efolds >= 70.) and (dS != None):
        valid = True
        
    #if dS != None:
    #out.writerow([b,c,w,R,t0,efolds,dS,dS_std,run,valid])
    global counter
    counter.value += 1
    #print counter.value
    sys.stdout.flush()
    sys.stdout.write("\r{0}".format(counter.value))
    sys.stdout.flush()
    return [b,c,w,R,t0,efolds,dS,dS_std,run,valid]
    
def mp_handler():    
    counter = Value('i', 0)
    pool = Pool(initializer = init, initargs= (counter, ))              # process per core
    #pool.map(calculate_inflation, val_array)
    with open(filename,'a') as f:
        out = writer(f)
        for results in pool.imap(calculate_inflation, val_array):
            if results[6] != None:
                out.writerow(results)
                
    print "\nFinished all %i calculations" % samp
    print "Written in File: %s" % filename
    
        
        


if __name__ == '__main__':
    #b,c,w,R,t0 
    filename =  sys.argv[1]
    DATA_PATH = os.path.dirname(filename)
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)

    samp = int(sys.argv[2])

#    val_array = np.asarray([1*10**np.random.uniform(-10,-15,samp),
#                           1*10**np.random.uniform(-10,0,samp),
#                            np.random.uniform(0,.5,samp),
#                            1*10**np.random.uniform(20,50,samp),
#                            1*10**np.random.uniform(-12,-10,samp)]).T
                  
    val_array = np.asarray([1.*np.random.uniform(1.0e-10,-1.0e-15,samp),
                            1.*np.random.uniform(1.0e-10,0,samp),
                            np.random.uniform(0,.5,samp),
                            1.0*np.random.uniform(1.0e20,1.0e50,samp),
                            np.random.uniform(1.0e-12,1.0e-10,samp)]).T
                            
    t=np.linspace(1.,6000.0,100000 ,dtype='float64')*1.0e-13
    

    if not os.path.isfile(filename):
        with open(filename,'wb') as f:
            out = writer(f)
            out.writerow(['b','c','w','R',r't_0',r'N_e','dS','dS_std','running','valid?'])
    
    #f= open(filename,'a')
    #out = writer(f)
    mp_handler()
    #counter = Value('i', 0)
    #pool = Pool(initializer = init, initargs= (counter, ))              # process per core
    #pool.map(calculate_inflation, val_array)
    #f.close()