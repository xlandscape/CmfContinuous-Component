# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 11:09:04 2019

@author: smh
"""
import pandas as pd
import os

fpath = "c:/LandscapeModel2019/projects/benchmark/catch150_timeseriesCatchment_CVodeKLU/Timeseries/"

files = [i.split(".")[0] for i in os.listdir(fpath)]

for f in files:
    df = pd.read_csv(os.path.join(fpath,f+".csv"))
    df.set_index("key",inplace=True)
    columns = df.columns.tolist()
    if len([i for i in columns if i == "rain"])>0:
        print(f)
        df.to_csv(os.path.join(fpath,f+"_copy.csv"))
        cols =   ['time',  'qperc', 'qsurf', 'qdrain', 'concgw', 'concsw','concdrainage']
        df[cols].to_csv(os.path.join(fpath,f+".csv"))