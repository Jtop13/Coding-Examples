"""
Module containing simulated fluctuation (noise) code
"""
#Pull all methods from create
from create import *

import glob
import matplotlib.pyplot as plt

postfix = '_c'
outDir = '/home/jovyan/efs/tnarock/fluxrope_data/cc_noise/'

for phi in range(5,360,5):
    
    if ( phi != 180 ):
    
        print("Working on phi:", phi)
    
        for theta in range(-85,90,5):
            for y0 in range(-95,100,5):
                for h in range(0,2,1):

                    # h is either 0 or 1, model needs -1 or 1
                    if ( h == 0 ):
                        h=-1
        
                    # simulated fluxrope
                    data = ec_create_data(1., phi, theta, 0., y0, h, C10=1, By0=10, \
                                          R=0.07, tau=1.3, noise_type='fractal', epsilon=0, num=50)
                
                    # create file name
                    phis = str(phi)
                    thetas = str(theta)
                    y0s = str(y0)
                    hs = str(h)
                    fname = outDir + 'fluxrope_cc_noise_B10_' + phis + '_' + thetas + '_' + y0s + \
                            '_' + hs + postfix + '.csv'
                
                    # open file
                    f = open(fname, "w")
                
                    # write to file
                    bx = data[2,:]
                    by = data[3,:]
                    bz = data[4,:]
                
                    for i in range( len(bx) ):
                        line = createLine(bx[i], by[i], bz[i])
                        f.write(line)
                    
                    # close file
                    f.close()
                    
    else:
        pass


#Grab some information on generation success
allFiles = glob.glob(outDir + "*.csv")
print("Created", len(allFiles), "fluxrope files")

predicted = ec_create_data(1, 175, 10, 0., 95, 1.0, C10=1, By0=10, \
                           R=0.07, tau=1.3, noise_type='fractal', epsilon=0, num=50)
plt.plot( predicted[0,:], predicted[4,:])

predicted = ec_create_data(1, 175, 10, 0., 95, 1.0, C10=1, By0=10, \
                           R=0.07, tau=1.3, noise_type='none', epsilon=0, num=50)
plt.plot( predicted[0,:], predicted[4,:])