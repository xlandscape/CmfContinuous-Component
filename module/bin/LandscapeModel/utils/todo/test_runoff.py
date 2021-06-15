# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 11:09:45 2018

@author: smh
"""

import cmf
from numpy import transpose,arange
from pylab import plot,show,subplot,xlabel,ylabel,legend
import datetime

def tutorial_runoff(z_source,z_sink,convert,timestep,ksat,nManning, saturated_depth,soil):
    p = cmf.project()
    # Create cell with 1000m2 and surface water storage
    c = p.NewCell(0,0,z_source,1000,True)
    # Set puddle depth to 2mm
    c.surfacewater.puddledepth = 0.002
    # Add several soil layer with thin or thick layer
    if soil == "thin":
        depths = [.01,.02,.04,.06,.09,.12,.16,.2,.25,.3,.36,.42,.49,.56,.64,.72,.81,.9,1,1.1,1.21,1.32,1.44,1.5]
    elif soil== "thick":
        depths = arange(.1,1.6,.1)
    for d in depths:
        c.add_layer(d, cmf.VanGenuchtenMualem(Ksat=ksat))
    # Connect layers with richards equation
    c.install_connection(cmf.Richards)
    # create a groudnwater storage and connect
    groundwater =p.NewStorage('groundwater',x=0,y=0,z=97.5) 
    cmf.Richards(c.layers[-1],groundwater)  
    # set saturated depth
    c.saturated_depth = saturated_depth
    # Create outlet
    outlet = p.NewStorage('outlet',100,0,z_sink)
        #######################################################################        
    # create groundwater storage
#    groundwater = p.NewStorage('groundwater',  x=0,y=0,z=97.5) 
    # Create connection, distance is calculated from position
    con = cmf.KinematicSurfaceRunoff(c.surfacewater,outlet,flowwidth=100)
    # set rainfall, a good shower to get surface runoff for sure (100mm/day)
    c.set_rainfall(100)
    # set nManning
    c.install_connection(cmf.GreenAmptInfiltration)
    c.surfacewater.nManning = nManning
    # Create a solver
    solver = cmf.CVodeIntegrator(p,1e-8)
    # Calculate results
#    Time,Vsoil, Vsurf, qsurf,qinf,rain = transpose([(t,c.layers[0].volume, c.surfacewater.volume, outlet(t), c.layers[0](t),c.get_rainfall(t)) 
#                                 for t in solver.run(cmf.Time(1,1,2001),datetime.datetime(2001,1,1,23),timestep)])
#    slope = z_source -z_sink
#    return slope,sum(rain) / convert,sum(qsurf) / convert ,sum(qinf) / convert

    Time, fluxto, qsurf,v_outlet,rain = transpose([(t,c.surfacewater.flux_to(outlet,t), outlet.waterbalance(t),outlet.volume,c.get_rainfall(t)) 
                                 for t in solver.run(cmf.Time(1,1,2001),datetime.datetime(2001,1,1,23),timestep)])
    return Time, fluxto, qsurf,v_outlet,rain

###############################################################################
## compare time steps
#res_min = [tutorial_runoff(100,i,24*60,cmf.min,ksat=1,nManning=nManning,saturated_depth=saturated_depth,soil="thin") for i in range(70,105,5)]
#res_hrs = [tutorial_runoff(100,i,24,cmf.h,ksat=1,nManning=nManning,saturated_depth=saturated_depth,soil="thin") for i in range(70,105,5)]
#res_day = [tutorial_runoff(100,i,1,cmf.day,ksat=1,nManning=nManning,saturated_depth=saturated_depth,soil="thin") for i in range(70,105,5)]
#for i in res_min:
#    print("min slope: %.0f rain: %.0fmm qsurf: %.0fmm qinf: %.0fmm"%(i))
#for i in res_hrs:
#    print("hrs slope: %.0f rain: %.0fmm qsurf: %.0fmm qinf: %.0fmm"%(i))
#for i in res_day:
#    print("day slope: %.0f rain: %.0fmm qsurf: %.0fmm qinf: %.0fmm"%(i))


##############################################################################
# compare time steps
saturated_depth = 1.5
nManning        = 0.1
#print("thin layer")
#res_hrs = [tutorial_runoff(100,i,24,cmf.h,ksat=1,nManning=nManning,saturated_depth=saturated_depth,soil="thin") for i in [95,90,70]]
#for i in res_hrs:
#    print("hourly - slope: %.0f rain: %.2fmm qsurf: %.2fmm qinf: %.2fmm"%(i))

#print("\n\nthick layer")
#res_hrs = [tutorial_runoff(100,i,24,cmf.h,ksat=1,nManning=nManning,saturated_depth=saturated_depth,soil="thick") for i in [95,90,70]]
#for i in res_hrs:
#    print("hourly - slope: %.0f rain: %.2fmm qsurf: %.2fmm qinf: %.2fmm"%(i))
#

convert = 1
print("\n\n\n################ Hourly ################")
Time, fluxto, qsurf,v_outlet,rain= tutorial_runoff(100,90,24,cmf.h,ksat=0.1,nManning=nManning,saturated_depth=saturated_depth,soil="thin")
V_diff = [0]+ list(v_outlet[1:]-v_outlet[:-1])
for t,r,ft,q,vd in zip(Time,rain,fluxto,qsurf,V_diff):
    print(t,"rain %.2fmm   fluxto %.2fmm    qsurf %.2fmm    qdiff %.2fmm"%(r/convert,ft/convert,q/convert,vd))
print("\nSummary 1 day")
print("rain %.2fmm    fluxto %.2fmm    qsurf %.2fmm    qdiff %.2fmm" % (sum(rain)/convert,sum(fluxto)/convert,sum(qsurf)/convert,sum(V_diff)))



convert = 1
print("\n\n\n################ Daily ################")
Time, fluxto, qsurf,v_outlet,rain= tutorial_runoff(100,90,24,cmf.day,ksat=0.1,nManning=nManning,saturated_depth=saturated_depth,soil="thin")
V_diff = [0]+ list(v_outlet[1:]-v_outlet[:-1])
for t,r,ft,q,vd in zip(Time,rain,fluxto,qsurf,V_diff):
    print(t,"rain %.2fmm   fluxto %.2fmm    qsurf %.2fmm    qdiff %.2fmm"%(r/convert,ft/convert,q/convert,vd))
print("\nSummary 1 day")
print("rain %.2fmm    fluxto %.2fmm    qsurf %.2fmm    qdiff %.2fmm" % (sum(rain)/convert,sum(fluxto)/convert,sum(qsurf)/convert,sum(V_diff)))



