# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 14:23:25 2019

@author: smh
"""

import datetime
import os

#   
fpath = "C:/LandscapeModel2019/projects/Rummen_subCatch_20reaches/medium_v01_cmpB_minute/Timeseries_hour/"
files = os.listdir(fpath)

for fname in files:
    print(fname)
    # open file and read        
    f = open(os.path.join(fpath,fname),"r")
    dat= f.read()
    f.close()
    dat = [d.split(",") for d in dat.split("\n")[:-1]]
    header = ",".join(dat[0])
    dat = dat[1:]
    # create minutes
    res =  [d for d in dat for i in range(60) ] 
    times = [datetime.datetime.strptime(t[1],"%Y-%m-%dT%H:%M") for t in dat]
    times = [datetime.datetime(t.year,t.month,t.day,t.hour,minute) for t in times for minute in range(0,60)]
    times = [t.strftime("%Y-%m-%dT%H:%M") for t in times]
    res  = [[r[0],t,r[2],r[3]] for r,t in zip(res,times)]
    # save file
    trg = "C:/LandscapeModel2019/projects/Rummen_subCatch_20reaches/medium_v01_cmpB_minute/Timeseries/"
    f = open(os.path.join(trg,fname),"w")
    s = header + "\n"
    s+="\n".join([",".join(r) for r in res])
    f.write(s)
    f.close()



