## -*- coding: utf-8 -*-
#"""
#Created on Wed Jul 10 13:28:48 2019
#
#@author: smh
#"""
#
#import cmf
#import numpy as np
#import pandas as pd
#from datetime import datetime
#import matplotlib.pylab as plt
#
##set time
#begin = datetime(2000,1,1,12,1)
#end = datetime(2000,1,1,12,59)
#timestep = cmf.sec
#timerange =pd.date_range(begin,end,freq="S") #S
#
#runoff = np.zeros([len(timerange)])
#runoff[4] = 1000 #m3 10mm = 10L/m2 
## set 
#
## create project
#p=cmf.project()
##
## add some cells 
#xx,yy = np.indices([25,25])
#xx = np.concatenate(xx)
#yy = np.concatenate(yy)
#zz = np.array([x+y for x,y in zip(xx,yy)])
#
#zz[10]=5
#zz[22]=5
#zz[10]=5
#zz[10]=5
#zz[10]=5
#url = 'https://python-graph-gallery.com/wp-content/uploads/volcano.csv'
#data = pd.read_csv(url)
#
#from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
#import matplotlib.pyplot as plt
#import numpy as np
#
#
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#
#ax.plot_trisurf(xx, yy, zz)
#
##zz = np.array([[0, 1, 2, 3, 4],
##               [1, 1, 2, 3, 4],
##               [2, 2, 2, 3, 4],
##               [3, 3, 3, 3, 4],
##               [4, 4, 4, 4, 4]])
##zz = np.concatenate(zz)
#
##xx = np.array([1])
##yy = np.array([0])
##zz = np.array([1])
#
##
### create cells
##cells = []
##bcs = []
##for x,y,z in zip(xx,yy,zz):
##    c = p.NewCell(x,y,z,1,with_surfacewater=True)
##    bc = cmf.NeumannBoundary.create(c.surfacewater)
##    cells.append(c)
##    bcs.append(bc)
##
### connect all cells with each other
###cmf.connect_cells_with_flux(p, cmf.KinematicSurfaceRunoff)
###con = cmf.KinematicSurfaceRunoff(cells[1].surfacewater,cells[0].surfacewater,flowwidth=1)
##
##outlet = p.NewOutlet('outlet',0,0,0)
##con = cmf.KinematicSurfaceRunoff(cells[0].surfacewater,outlet,flowwidth=10)
##
##
### set flux
##flux = cmf.timeseries.from_sequence(begin,timestep,runoff)
###for bc in bcs:
###    bc.flux = flux
##
##bcs[0].flux = flux
##
### crate solver
##solvertype = vars(cmf)['CVodeKLU']    
##wsolver = solvertype(p, 1e-9)
##
### make simulation
##res=[]
##out = []
##timecheck_start_run = datetime.now()        
##for t in wsolver.run(begin,end,timestep):    
##    res.append([c.surfacewater.volume for c in p.cells])
##    out.append(outlet.waterbalance(t))
##    print(f'{datetime.now()- timecheck_start_run} {wsolver.t:%Y-%m-%d %H:%M}')
##    
##    
##    
##fig = plt.figure()
##
##ax = fig.add_subplot(111)
##
##ax.plot(out)
##
#
#
#
#
##
##
##import cmf
##from numpy import transpose
##from pylab import plot,show,subplot
##p = cmf.project()
### Create cell with 1000m2 and surface water storage
##c = p.NewCell(0,0,1,1000,True)
### Set puddle depth to 2mm
##c.surfacewater.puddledepth = 0.002
### Add a thick layer, low conductivity. Use Green-Ampt-Infiltration
##c.add_layer(0.1, cmf.VanGenuchtenMualem(Ksat=0.1))
##c.install_connection(cmf.GreenAmptInfiltration)
### Create outlet, 10 m from cell center, 1m below cell
##outlet = p.NewOutlet('outlet',10,0,0)
### Create connection, distance is calculated from position
##con = cmf.KinematicSurfaceRunoff(c.surfacewater,outlet,flowwidth=10)
### set rainfall, a good shower to get surface runoff for sure (100mm/day)
##c.set_rainfall(100.)
### Create a solver
##solver = cmf.CVodeIntegrator(p,1e-8)
### Calculate results
##Vsoil, Vsurf, qsurf,qinf = transpose([(c.layers[0].volume, c.surfacewater.volume, outlet(t), c.layers[0](t)) 
##                             for t in solver.run(cmf.Time(1,1,2012),cmf.Time(2,1,2012),cmf.min)])
### Present results
##ax1=subplot(211)
##plot(Vsurf,label='Surface')
##plot(Vsoil,label='Soil')
##plt.ylabel('Water content in mm')
##plt.legend(loc=0)
##subplot(212,sharex=ax1)
##plot(qsurf,label='Surface')
##plot(qinf,label='Soil')
##plt.ylabel('Flux in mm/day')
##plt.xlabel('Time in minutes')
##plt.legend(loc=0)
##
##
##
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

# library
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
 
# Get the data (csv file is hosted on the web)
url = 'https://python-graph-gallery.com/wp-content/uploads/volcano.csv'
data = pd.read_csv(url)
 
# Transform it to a long format
df=data.unstack().reset_index()
df.columns=["X","Y","Z"]
 
# And transform the old column name in something numeric
df['X']=pd.Categorical(df['X'])
df['X']=df['X'].cat.codes
 
# Make the plot
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.plot_trisurf(df['Y'], df['X'], df['Z'], cmap=plt.cm.viridis, linewidth=0.2)
plt.show()


https://stackoverflow.com/questions/42924993/colorbar-for-matplotlib-plot-surface-using-facecolors
 
## to Add a color bar which maps values to colors.
#surf=ax.plot_trisurf(df['Y'], df['X'], df['Z'], cmap=plt.cm.viridis, linewidth=0.2)
#fig.colorbar( surf, shrink=0.5, aspect=5)
#plt.show()
# 
## Rotate it
#ax.view_init(30, 45)
#plt.show()
# 
## Other palette
#ax.plot_trisurf(df['Y'], df['X'], df['Z'], cmap=plt.cm.jet, linewidth=0.01)
#plt.show()