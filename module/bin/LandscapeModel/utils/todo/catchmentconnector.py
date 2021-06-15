# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 13:34:48 2019

@author: smh
"""

import os
import LandscapeModel

if __name__ == "__main__":
    
    ###########################################################################
    # laod project 
    fname = "runlist.csv"
    key = "ExampleProject1"
    
    # get current path
    fdir = os.path.join(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]),"projects")   
    # read runlist
    runFactory = LandscapeModel.utils.RunFactory(fdir,fname=fname)
    # setup catchment
    runFactory.setup(key)
    catchment = runFactory.runs[0]
    
    ###########################################################################
    # create pre-porcessing object and run separatiom
    catchcon = LandscapeModel.utils.PreProcessing.CatchmentConnector(catchment,
                                                                     simplify_connections=4,
                                                                     connection_type="RO_GW")
    
    # plot results of separation
    catchcon.makePlot("test_network.png",resX=100,resY=100,plotVoroni=False,
                      plotElevation=True,plot_simplified=True)
    catchcon.makePlot("test_voroni.png",resX=100,resY=100,plotVoroni=True,
                      plotElevation=False,plot_simplified=True)