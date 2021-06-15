# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 09:55:38 2018

@author:    smh
"""

import LandscapeModel
from datetime import datetime
import os

if __name__ == "__main__":
    
    ###########################################################################
    # load existing setup
    fpath = "C:/landscapeModel2019/projects"
    fname = "runlist"
    key = "csv_areayieldCatchment_Rummen"

    ###########################################################################
    # pre-processing
    
    # create connections between cells<>cells and cells<>reches
    catchcon = LandscapeModel.utils.PreProcessing.CatchmentConnector(
                                                    os.path.join(fpath,key),
                                                    simplify_connections=4,
                                                    connection_type="RO_GW")
    # plot results of connections
    catchcon.makePlot(os.path.join(fpath,key,"flow_network_voroni.png"),resX=100,resY=100,plotVoroni=True,
                    plotElevation=False,plot_simplified=True,fontsize=4,markersize=0.5)
    catchcon.makePlot(os.path.join(fpath,key,"flow_network.png"),resX=100,resY=100,plotVoroni=False,
                    plotElevation=True,plot_simplified=True,fontsize=4,markersize=0.5)

#    # calculate area-weighted flow timeseries of reach each and create files
#    ayc = LandscapeModel.utils.PreProcessing.AreaYieldCatchment(
#                                                fpath,
#                                                key,
#                                                frunlist="runlist",
#                                                filetype = "csv",
#                                                time_format="%Y-%m-%dT%H:%M")
#    
#    data_resampled=ayc.create_timeseries(resample_rule="1H",
#                                         resample_type="interpolate")
#
#    # create scenarios (365 days dry 10%-percentile, medium 50%-percentile and 
#    # wet 90%-percentile year) and create files
#    ayc.create_timeseries_scenarios(resample_rule="1H",
#                                         resample_type="interpolate")

#    ###########################################################################
#    # simulation  
    
#    # read runlist
#    runFactory = LandscapeModel.utils.RunFactory(fpath,fname)
#    # create a setup based on existing data
#    runFactory.setup(key)
#    # get model run
#    catchment = runFactory.runs[0]

#    runFactory(key)
#    
#    ##########################################################################
#    # post-processing
#    
#     initialise pre-porcessing object with existing catchment
#    pstPrc = LandscapeModel.utils.PostProcessing.AreaYieldCatchment(catchment)
#    # plot observed versus simulated flow
#    pstPrc.performance("flow")
#
#    # plot histogramm of hydrological parameter across catchment
#    pstPrc.catchment_hydrology()
#    
#    # plot cumulative distribution function of PEC values across catchment
#    pstPrc.catchment_efate(datetime(1900,5,10,10),[1,2,4,8,16,24],
#                           maxSW=.4,maxSED=.05)
#    