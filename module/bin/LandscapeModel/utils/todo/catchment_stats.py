# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 09:55:38 2018

@author:    smh
"""

import os
import LandscapeModel
import sys
from datetime import datetime

if __name__ == "__main__":

#    # get system arguments
#    args = (sys.argv)
#    fname = args[1] 
#    key = args[2] 
#    
##    fname = "runlist"
##    key = "csv_separated_completeCatchment_Velm"
#
#    # get current path
#    fdir = os.path.join(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]),"projects")   
#    # read runlist
#    runFactory = LandscapeModel.utils.RunFactory(fdir,fname=fname)
#    #make simulation
#    start = datetime.now()
#    runFactory(key)
#    print("runtime:",datetime.now()-start)
    

    
    import pandas as pd
    import numpy as np
    import matplotlib.pylab as plt
    import matplotlib.patches as mpatches
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    
     load flow data
    fname = r"c:\LandscapeModel2019\projects\csv_areayieldCatchment_Rummen_medium\csv_areayieldCatchment_Rummen_medium_reaches.csv"
    data = pd.read_csv(fname)
    data.to_hdf(r"c:\LandscapeModel2019\projects\csv_areayieldCatchment_Rummen_medium\csv_areayieldCatchment_Rummen_medium_reaches.hdf",key="reaches")
    data = pd.read_hdf(r"c:\LandscapeModel2019\projects\csv_areayieldCatchment_Rummen_medium\csv_areayieldCatchment_Rummen_medium_reaches.hdf")
    # convert strign date to datetime
    data["time"] = pd.to_datetime(data ["time"],format="%Y-%m-%dT%H:%M")
    data.set_index("time",inplace=True)
    
    # load spraydrift data
    spraydrift = pd.read_csv(r"c:\LandscapeModel2019\projects\csv_areayieldCatchment_Rummen_medium\SprayDriftList.csv")
    
    # select data
    res = data[(data.index.day ==10) & (data.index.month == 5)]
    res = data[data["key"].isin(spraydrift.key.tolist())]

    # make plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(221)
    ax.hist(data.depth,color="k",alpha=.5,normed=True,label="Catchment")
    ax.hist(res.depth,color="orange",alpha=.5,normed=True,label="Appl. day, treated fields")
    ax.set_xlabel("Depth [m]")
    ax.text(.5,.95,'(a)',fontweight="bold",
        horizontalalignment='center',
        transform=ax.transAxes)
    ax.legend(loc=0,bbox_to_anchor=(0.00, 0.5, 1., .102),fontsize="small")

    ax = fig.add_subplot(222)
    ax.hist(data.volume,color="k",alpha=.5,normed=True)
    ax.hist(res.volume,color="orange",alpha=.5,normed=True)
    ax.set_xlabel("Volume [m]")
    ax.text(.5,.95,'(b)',fontweight="bold",
        horizontalalignment='center',
        transform=ax.transAxes)

    ax = fig.add_subplot(223)
    ax.hist(data.flow,color="k",alpha=.5,normed=True)
    ax.hist(res.flow,color="orange",alpha=.5,normed=True)
    ax.set_xlabel("Flow [m³]")
    ax.text(.5,.95,'(c)',fontweight="bold",
        horizontalalignment='center',
        transform=ax.transAxes)

    ax = fig.add_subplot(224)
    ax.hist(data.area,color="k",alpha=.5,normed=True)
    ax.hist(res.area,color="orange",alpha=.5,normed=True)
    ax.set_xlabel("Wet area [m²]")
    ax.text(.5,.95,'(d)',fontweight="bold",
        horizontalalignment='center',
        transform=ax.transAxes)

    plt.tight_layout()
    fig.savefig("hydrology.png",dpi=1000,transparent=True) 
    
    
    
    
    
    
    
    
