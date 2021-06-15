# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 10:36:31 2019

@author: smh
"""

import LandscapeModel
import matplotlib.pylab as plt
import os

if __name__ == "__main__":
    io=LandscapeModel.utils.Tools.IO()
        
    # open runlist
    fpath ="c:/_CatchmentModel_v093/projects/test_solver/"
    fname = "test_solver"
    runlist = LandscapeModel.utils.ParameterList(fpath,fname,",")
    
    # get simlauted data
    sim = [io.read_csv_to_pandas(os.path.join(i.fpath,i.key,i.key+"_reaches.csv"),
                                 keys=["time","key"],time_key="time") for i in runlist]
    
    # get MASS_SW (mg/m³) for each run of reach r656 (upstream outlet)
    MASS_SW = [i.loc[(slice(None),["r656"]),["MASS_SW"]] for i in sim]
    PEC_SW = [i.loc[(slice(None),["r656"]),["PEC_SW"]] for i in sim]

    # plot MASS_SW
    fig = plt.figure(figsize=(10,15))  
    nsub = len(runlist)
    time = MASS_SW[0].index.levels[0]
    for i,key in enumerate(runlist):
        ax = fig.add_subplot(nsub,1,i+1)
        ax.plot(time,MASS_SW[i],label=key.key,color="k")
        ax.grid(True)
        ax.legend(loc=2)
        ax.set_xlabel("time")
        ax.set_ylabel("MASS SW mg/m³")
        mass_sum = MASS_SW[i].sum()
        mass_max = MASS_SW[i].max()
        pec_max = PEC_SW[i].max()
        ax.text(0.1,0.4,"Sum Mass SW: %.3f\nMax Mass SW: %.3f\nMAX PEC: %.3f"%(mass_sum,mass_max,pec_max),
                transform=ax.transAxes)    
    plt.tight_layout()      
    plt.savefig(os.path.join(fpath,"MASS_SW.png"),dpi=300) 