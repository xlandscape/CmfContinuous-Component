# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 09:55:38 2018

@author:    smh
"""

import LandscapeModel
from datetime import datetime

if __name__ == "__main__":
    
    ###########################################################################
    # load existing setup
    fpath = "C:/"
    fname = "runlist.csv"
    key = "ExampleProject1"
    
    # read runlist
    runFactory = LandscapeModel.utils.RunFactory(fpath,fname)
       
    # create a setup based on existing data
    runFactory.setup(key)
    # get model run
    catchment = runFactory.runs[0]
    
    ###########################################################################
    # pre-processing

    # ....    

    ###########################################################################
    # simulation
    runFactory(key)

    ###########################################################################
    # post-processing
    
    # plot results of fields
    plots = LandscapeModel.utils.Plotting()
    for cell in catchment.inpData.CellList:
        # Sankey plot of field water balance
        plots.FieldWaterBalance(catchment,cell.key,title=key,fpath="C:/.../"+key)
        # Canopy processes
        plots.plot_PlantGrowth(catchment,cell.key,title=key,fpath="C:/.../"+key)  