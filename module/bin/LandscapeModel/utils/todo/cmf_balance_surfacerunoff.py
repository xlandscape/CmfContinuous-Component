# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 14:57:35 2018

@author: smh
"""

import cmf
from datetime import datetime,timedelta
import pandas as pd

def balance_runoff(thickness_layer1,slope, flowwidth,nManning,x_field,y_field,
                   x_bucket,y_bucket,z_bucket,
                                 Ksat,phi,alpha,n,rainfall_rate):
    
    """
    Creates a project with one cell and one layer. The surface water storage
    of the cell is connected with an additional storage which serves as a bucket
    to balance the surface water runoff.
    
    slope (%):              slope of the field
    flowwidth (m):          flowwidth of surface runoff
    nManning (-):           Mannings's roughness coefficient
    x_field (m):            x-ccordiante of field
    y_field (m):            y-ccordiante of field
    z_field (m):            z-ccordiante of field
    Ksat (m/s):             Saturated hydraulic conductivity
    phi (-):                Porosity
    alpha (-):              van Genuchten alpha
    n (-):                  van Genuchten n
    rainfall_rate (mm):     constant rainfall
    
    Returns a table with the following information:
        
    'Rain [mm/day]'             Rainfall rate
    'SW --> Bucket [mm/day]'    Surface water runoff
    'SW --> Soil [mm/day]'      Infiltration into soil
    'SW volume [mm]'            Water volume surface water volume
    'Bucket volume [mm]'        Water volume bucket
    'Bucket volume change [mm]  Change of water volume in bucket
    'Soil volume [mm]'          Water volume soil
    'Soil volume change [mm]'   change of water volume in soil
    
    """
    
    # create project
    p = cmf.project()
    
    # create cell a coordiantes 10,10,10 (x,y,z) with an area of 1000m² and surface water storage
    cell = p.NewCell(x=x_field,y=y_field,z=z_field,area=1000, with_surfacewater=True)
    
    # setup an retention curve
    r_curve = cmf.VanGenuchtenMualem(Ksat=Ksat,phi=phi,alpha=alpha,n=n)
    
    # install one soil layer with a thicness of 1m
    l1 = cell.add_layer(thickness_layer1,r_curve)
    cell.install_connection(cmf.Richards)
    
    # install an infiltration connection
    cell.surfacewater.puddledepth = 0.002
    cell.install_connection(cmf.GreenAmptInfiltration)

    # create a bucket for surface water
    bucket = p.NewStorage('bucket',x=x_bucket,y=y_bucket,z=z_bucket)
    cmf.KinematicSurfaceRunoff(cell.surfacewater,bucket,flowwidth=flowwidth) 
    
    # set Manning's riughness coefficient
    cell.surfacewater.nManning = nManning # default

    #set a contant rainfall rate
    cell.set_rainfall(rainfall_rate)

    # create solver
    solver = cmf.CVodeIntegrator(p,1e-6)
    solver.t = cmf.Time(1,1,2011)

    soil_volume_t0 = l1.volume
    bucket_volume_t0 = 0
    # run model
    res = []
    for t in solver.run(solver.t,solver.t + timedelta(days=1),timedelta(hours=1)):
        
        soil_volume_change = l1.volume - soil_volume_t0
        bucket_volume_change = bucket.volume - bucket_volume_t0
        
        
        sw_to_bucket = cell.surfacewater.flux_to(bucket,t)/24.
        sw_to_soil = cell.surfacewater.flux_to(l1,t)/24.
        res .append((t.AsPython(),cell.get_rainfall(t)/24.,sw_to_bucket,sw_to_soil,
                     cell.surfacewater.volume,bucket.volume,bucket_volume_change,
                     l1.volume,soil_volume_change))
        soil_volume_t0 = l1.volume
        bucket_volume_t0 = bucket.volume

    #create dataframe 
    res = pd.DataFrame(res,columns=["Time","Rain [mm/hour]","SW --> Bucket [mm/hour]",
                                    "SW --> Soil [mm/hour]","SW volume [mm]",
                                    "Bucket volume [mm]","Bucket volume change [mm]",
                                    "Soil volume [mm]","Soil volume change [mm]"])
    res.set_index("Time",inplace=True)

    return res




if __name__ == "__main__":
    
    # The aim of the script is to assess the surface runoff of a single field in 
    # relattion to a given flowwidth, slope and Manning's roughness coefficient.
    # The has one layer and a surface water storage; the latter one is connected
    # with anotehr storages which collects all water form the sw-storage
    
    # thickness layer 1
    thickness_layer1 = 0.01
    
    # coordinates of field (m)
    x_field  = 10
    y_field = 10
    z_field = 10

    # hydraulic properties
    Ksat = .1
    phi = 0.5
    alpha = 0.01
    n = 1.5
    
    # rainfall rate
    rainfall_rate = 200

    for slope in [1,5,10,50]: # slope (%)
        for flowwidth in [10,50,100,1000]: # flowwidth (m)
            for nManning in [0.01,0.19,0.6]:# Manning's roughness coefficient: fallow (no residue), convential tillgage (residue), rangeland (2ß% cover) (SWAT theory manual, 2009)
                
                # coordiantes of virtual bucket storage
                x_bucket = x_field+flowwidth 
                y_bucket = y_field
                z_bucket = z_field-(z_field*slope/100) 
                
                # conduction model run for one day in hourly timestep
                res = balance_runoff(thickness_layer1,slope, flowwidth,nManning,x_field,y_field,
                                     x_bucket,y_bucket,z_bucket,
                                             Ksat,phi,alpha,n,rainfall_rate)
                print("slope: %.0f flowwidth: %.0f nManning: %.3f rain: %.2fmm bucket: %.2fmm soil %.2fmm" % 
                      (slope,flowwidth,nManning,res["Rain [mm/hour]"].sum(),res["Bucket volume change [mm]"].sum(),res["Soil volume change [mm]"].sum()))        
            
            
        
        
        
        
        
        