# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 13:28:58 2018

@author: smh
"""

import cmf
import pandas as pd
import numpy as np

class DriftCalculator():
    """
    Class which connects the Landscape Model with a drift calculation. Drift
    can be loaded from a timeseries or being calculated during runtime
    Calculates wind drift input into a river segment from an related field.
    
    In the simplest implementation of the drift class all data is given as time
    series for each river segment of the catchmanet.
    """
    def __init__(self,catchment):
        """
        Setup of drift module.  
        
        catchment (Subcatchment):   Catchment which holds the drift object.
        """
        
        self.catchment = catchment
        reaches = self.catchment.reaches

        #load drift dataset
        data = pd.read_csv(self.catchment.inputdata_path + "/" + self.catchment.name+ "_Drift.csv")
        #get list with drift receiving river segments
        river_segments = pd.unique(data["name"])
        for name in river_segments:
            
            
            #get drift values for one river segment
            river_drift = data[data["name"]==name]
            #find reach         
            reach = reaches[[i.Name for i in reaches].index(name)]
            # get drift load from time series in [mg]
            drift_load = river_drift["drift load [mg]"]
            # create time series with water fluxes of 1m3
            drift_flux  = river_drift["drift flux [m3]"]

            
            #create cmf time series
            fluxs = cmf.timeseries.from_sequence(self.catchment.begin ,self.catchment.timestep,drift_flux)
            concs =  cmf.timeseries.from_sequence(self.catchment.begin ,self.catchment.timestep,drift_load)
            #set flux of reach            
            reach.nbc.flux = fluxs
            reach.nbc.concentration[self.catchment.substance] = concs  
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        