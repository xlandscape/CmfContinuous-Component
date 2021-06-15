# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 09:55:38 2018

@author:    smh
"""
#0:00:02.253225
import os
import LandscapeModel
import sys
from datetime import datetime

if __name__ == "__main__":

    # get system arguments
    args = (sys.argv)    
    fname = args[1]
    if len(args) > 2:
        key = args[2]
    else:
        key = 'None'

    # Try if the runlist is given with a full path name
    if os.path.exists(fname):
        fdir = os.path.abspath(os.path.dirname(fname))
        # Strip path from fname
        fname = os.path.basename(fname)
        # Remove extension
        if fname.endswith('.csv'):
            fname = fname[:-4]
    # else look for projects in working directory
    elif os.path.exists('projects'):
        fdir = 'projects'
    else:
        #  Get home directory relative to this script path
        homedir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '..'
            ))
        # get current path
        fdir = os.path.join(homedir, "projects")

    #########################################################################
    # read input dat aand simulate   
    runFactory = LandscapeModel.utils.RunFactory(fdir,fname)
    runFactory(key,printMessage=False,
               plotMap=True,
               printCatchmentOutput=False,
               printFieldOutput=False,
               printTime=False)    

##    ###########################################################################
##    # post-processing
#    catchment = runFactory.runs[-1]
#    # initialise pre-porcessing object with existing catchment
#    pstPrc = LandscapeModel.utils.PostProcessing.AreaYieldCatchment(catchment)
###
##    # plot histogramm of hydrological parameter across catchment
##    pstPrc.catchment_hydrology()
##    
##    # plot cumulative distribution function of PEC values across catchment
##    pstPrc.catchment_efate(datetime(2007,5,2,10),[1,2,3,4,5,6],
##                           maxSW=.4,maxSED=1)
##    
#    # plot 3-D plot of two reach variables, e.g. PEC_SW and flow
#    pstPrc.branch_hydrology_and_efate("PEC_SW",
#                                           "PEC$_{SW}$ [$\mu$g L$^{-1}$]",
#                                           "flow",
#                                           "Flow [m³ sec$^{-1}$]",
#                                           reach_start="r136",reach_end="r282",
#                                           tstart = datetime(2007,5,2,8),
#                                           tend = datetime(2007,5,3,23),
#                                           tintverval = 4,
#                                           timescale="hourly",
#                                           vmin=None,vmax=None,fname="1")
#
#    # plot 3-D plot of two reach variables, e.g. PEC_SW and flow
#    pstPrc.branch_hydrology_and_efate("PEC_SW",
#                                           "PEC$_{SW}$ [$\mu$g L$^{-1}$]",
#                                           "flow",
#                                           "Flow [m³ sec$^{-1}$]",
#                                           reach_start="r303",reach_end="r300",
#                                           tstart = datetime(2007,5,2,8),
#                                           tend = datetime(2007,5,3,23),
#                                           tintverval = 4,
#                                           timescale="hourly",
#                                           vmin=None,vmax=None,fname="1")
#
#    # plot 3-D plot of two reach variables, e.g. PEC_SW and flow
#    pstPrc.branch_hydrology_and_efate("PEC_SW",
#                                           "PEC$_{SW}$ [$\mu$g L$^{-1}$]",
#                                           "flow",
#                                           "Flow [m³ sec$^{-1}$]",
#                                           reach_start="r281",reach_end="r284",
#                                           tstart = datetime(2007,5,2,8),
#                                           tend = datetime(2007,5,3,23),
#                                           tintverval = 4,
#                                           timescale="hourly",
#                                           vmin=None,vmax=None,fname="1")
##    
#    pstPrc.reach_hydrology_and_efate("r284",tstart=datetime(2007,5,2,8),
#                                     tend=datetime(2007,5,3,23),
#                                  ymax=[0.15,4,0.5,20],
#                                  maxconc=5.,
#                                  maxload=5.)  
#
#    pstPrc.reach_hydrology_and_efate("r282",tstart=datetime(2007,5,2,8),
#                                 tend=datetime(2007,5,3,23),
#                              ymax=[0.15,4,0.5,20],
#                              maxconc=5.,
#                              maxload=5.)  
#        
#        
#    pstPrc.reach_hydrology_and_efate("r300",tstart=datetime(2007,5,2,8),
#                             tend=datetime(2007,5,3,23),
#                          ymax=[0.15,4,0.5,20],
#                          maxconc=5.,
#                          maxload=5.)  
##    
