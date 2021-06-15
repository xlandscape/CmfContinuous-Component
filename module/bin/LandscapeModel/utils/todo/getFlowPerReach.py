# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 15:48:55 2018

@author: smh
"""

import pandas as pd

###############################################################################
# create discharge data for eachreach

## read flow data
flow = pd.read_csv(r"c:\LandscapeModel\inStreamRummen\Mielen-boven-Aalst Melsterbeek_Discharge.csv")
flow["time"] = pd.to_datetime(flow["time"])
flow.set_index("time",inplace=True)
flow=flow.resample("H")
flow=flow.interpolate(method='linear')
flow["date_as_string"] = [i.strftime("%Y-%m-%dT%H:%M") for i in flow.index]
flow_period = flow[(flow.index >= pd.Timestamp("2007-01-01")) & (flow.index <=  pd.Timestamp("2008-01-01"))][:-1]

# read areas
reacharea = pd.read_csv(r"c:\LandscapeModel\inStreamRummen\reach_sourcearea.csv")

# make files
for index, reach in reacharea.iterrows():
    print(reach.reach)
    new = pd.DataFrame()
    new["time"] = flow_period["date_as_string"]
    new["flow_m3day"] = flow_period['flow (mm/day)']  / 1000. *  reach.area
    new["key"] =  reach.reach
    new.set_index("key",inplace=True)
    new.to_csv("c:/LandscapeModel/inStreamRummen/TimeSeries/"+reach.reach+".csv")


    
    
    