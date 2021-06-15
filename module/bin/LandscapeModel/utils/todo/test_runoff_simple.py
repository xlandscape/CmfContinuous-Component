# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 11:09:45 2018

@author: smh
"""

import cmf
from numpy import transpose
import datetime

def tutorial_runoff(ksat,nManning,flowwidth):
    p = cmf.project()
    # Create cell with 1000m2 and surface water storage
    c = p.NewCell(0,0,100,1000,True)
    # Set puddle depth to 2mm
    c.surfacewater.puddledepth = 0.002
    # Add several soil layer with thin or thick layer
    depths = [.01,.02,.04,.06,.09,.12,.16,.2,.25,.3,.36,.42,.49,.56,.64,.72,.81,.9,1,1.1,1.21,1.32,1.44,1.5]
    for d in depths:
        c.add_layer(d, cmf.VanGenuchtenMualem(Ksat=ksat))
    # Connect layers with richards equation
    c.install_connection(cmf.Richards)
    # Create outlet
    outlet = p.NewStorage('outlet',100,0,90)
    # Create connection
    cmf.KinematicSurfaceRunoff(c.surfacewater,outlet,flowwidth=flowwidth)
    # infiltration    
    c.install_connection(cmf.GreenAmptInfiltration)
    # set nManning
    c.surfacewater.nManning = nManning
    # set rainfall, a good shower to get surface runoff for sure (100mm/day)
    c.set_rainfall(100)
    # Create a solver
    solver = cmf.CVodeIntegrator(p,1e-8)
    # Calculate results
    Time, qsurf,rain = transpose([(t, outlet.waterbalance(t),c.get_rainfall(t)) 
                                 for t in solver.run(cmf.Time(1,1,2001),datetime.datetime(2001,1,1,23),cmf.h)])
    return p,c,Time, qsurf/24,rain/24 # convert daily values to hourly


##############################################################################
# check flowwidth (all layers have the same Ksat value)
nManning        = 0.1 # [-]
ksat            = 0.01 # [m/day]
# make runs
for flowwidth in [1,10,100,500,1000]: # [m]
    print("\n\n\n################ 1day runtime, flowwidth: " + str(flowwidth) + "m ################")
    prj,cell,Time, qsurf,rain= tutorial_runoff(ksat,nManning,flowwidth)
    for t,r,q in zip(Time,rain,qsurf): print(t,"rain %.2fmm/h   qsurf %.2fmm/h"%(r,q))
    print("-------------------------------------------")
    print("Sum                 rain %.2fmm   qsurf %.2fmm" % (sum(rain),sum(qsurf)))



##############################################################################
# check ksat
nManning        = 0.1 # [-]
flowwidth       = 100 # [m]
# make runs
for ksat in [0.01,0.1,1,5,10]: #[m/day]
    print("\n\n\n################ 1day runtime, ksat: " + str(ksat) + "m/day ################")
    prj,cell,Time, qsurf,rain= tutorial_runoff(ksat,nManning,flowwidth)
    for t,r,q in zip(Time,rain,qsurf): print(t,"rain %.2fmm/h   qsurf %.2fmm/h"%(r,q))
    print("-------------------------------------------")
    print("Sum                 rain %.2fmm   qsurf %.2fmm" % (sum(rain),sum(qsurf)))














