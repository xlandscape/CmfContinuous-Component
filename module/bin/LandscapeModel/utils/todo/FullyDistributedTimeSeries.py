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
    
    # create connections between cells<>cells and cells<>reches
    catchcon = LandscapeModel.utils.PreProcessing.CatchmentConnector(catchment,
                                                    simplify_connections=4,
                                                    connection_type="RO_GW")
    # plot results of separation
    catchcon.makePlot("test_network.png",resX=100,resY=100,plotVoroni=False,
                    plotElevation=True,plot_simplified=True)

    # optional: separate the catchment into sub-units and make simulations
    catchSep = LandscapeModel.utils.CatchmentSeparator(catchment)
    catchSep()
    catchSep.plotMap(fontsize=8,withnames=True)

    ###########################################################################
    # option1: simulation
    catchSep.run_SolverUnits()

    # without separation:
    runFactory(key)

    # note that the catchment separation function can be also activated in
    # the runlist.csv. In that case, the function above can be used as well

    ###########################################################################
    # post-processing
    
    # initialise pre-porcessing object with existing catchment
    pstPrc = LandscapeModel.utils.PostProcessing.AreaYieldCatchment(catchment)

    # plot observed versus simulated flow
    pstPrc.performance("flow")

    # plot histogramm of hydrological parameter across catchment
    pstPrc.catchment_hydrology()
    
    # plot cumulative distribution function of PEC values across catchment
    pstPrc.catchment_efate(datetime(1900,5,10,10),[1,2,4,8,16,24],
                           maxSW=.4,maxSED=.05)
