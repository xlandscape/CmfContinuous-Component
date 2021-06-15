# -*- coding: utf-8 -*-
"""
Created on Thu May 16 13:45:52 2019

@author: smh
"""
import pandas as pd
#from LandscapeModel.utils import IO 
#from datetime import datetime
#
#fname = r"c:\LandscapeModel2019\projects\test\hdf_areayieldCatchment_Velm_medium_cmpB_reaches.hdf"
#io=IO()
#
#res = io.read_hdf_to_pandas(fname=fname, keys=["time","key"],  dset="reaches",
#                            time_key="time", time_format="%Y-%m-%dT%H:%M",
#                            convert_byte=["time","key"])

drift = pd.read_csv(r"c:\LandscapeModel2019\projects\test\SprayDriftList.csv")
drift.set_index("key",inplace=True)
reaches = pd.read_csv(r"c:\LandscapeModel2019\projects\test\ReachList.csv")
reaches.set_index("key",inplace=True)

# water surface at day of application




applied = pd.merge(reaches, drift, how='inner', on=None, left_on=None, right_on=None,
         left_index=True, right_index=True, sort=True,
         suffixes=('_x', '_y'), copy=True, indicator=False,
         validate=None)

area = pd.merge(applied, app, how='inner', on=None, left_on=None, right_on=None,
         left_index=True, right_index=True, sort=True,
         suffixes=('_x', '_y'), copy=True, indicator=False,
         validate=None)

input_SW = applied.rate * area.area
print("input sw", input_SW.sum())



app = res.loc[datetime(1900,5,10,10)]
print("5th May MASS SW", app["MASS_SW"].sum())
print("5th May MASS SED", app["MASS_SED"].sum())
print("percentage sediment:", app["MASS_SED"].sum() / input_SW.sum()*100)


app = res.loc[datetime(1900,12,31,23)]

print("31st DEC MASS SW", app["MASS_SW"].sum())
print("31st DEC MASS SED", app["MASS_SED"].sum())
print("percentage sediment:", app["MASS_SED"].sum() / input_SW.sum()*100)

print("faction sw after 10 days",res.loc[datetime(1900,5,11,12)]["MASS_SW"].sum()/input_SW.sum()*100)


res.loc[datetime(1900,5,2,9):datetime(1900,5,20,23)]["MASS_SW"].groupby(level=[0]).sum().plot()
res.loc[datetime(1900,5,2,9):datetime(1900,5,20,23)]["MASS_SED"].groupby(level=[0]).sum().plot()