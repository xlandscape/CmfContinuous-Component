# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 08:19:50 2019

@author: smh
"""

import os
import argparse
from pathlib import Path
from STEPSRiverNetwork import STEPSRiverNetwork

def get_fdir(subfolder):
    """
    Return current working directoy and add subfolder to path.
    """
    fdir = os.path.abspath(os.path.join(
                    os.path.dirname(Path(__file__).parent),
                    *subfolder))
    return fdir

FLAGS = None

if __name__ == "__main__":
    
    ###########################################################################
    # get command line arguments or use default
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder',type=str, default=get_fdir(["projects"]),
                        help='Path of project folder.')
    parser.add_argument('--runlist',type=str,default='runlist',
                        help='Filename of runlist.')
    parser.add_argument('--key',type=str,default='',
                        help='Name of model run')
    FLAGS, unparsed = parser.parse_known_args()
            
    ###########################################################################
    # run steps for specific project and key

#    fpath =  "c:/LandscapeModel2019/projects/Rummen_subCatch_20reaches/"
#    key = "hydro_v01_medium_minute"
#    key = "hydro_v01_medium_hour"
#    filetype="csv"

    # create model  
    print("model setup")
    sRN = STEPSRiverNetwork(FLAGS.folder,FLAGS.key,"csv",
                             DEGHL_SW_0=1000,DEGHL_SED_0=43.9,KOC=1024000,
                             Temp0=21.,Q10=2.2, DENS=0.8,POROSITY=0.6,OC=0.05,
                             DEPTH_SED=0.05, DEPTH_SED_DEEP=0.45,
                             DIFF_L_SED=0.005,DIFF_L=0.005,DIFF_W=4.3*(10**-5),
                             convertDeltaT=24.*60) # the DT values are per day, so convert to minutes

    # make model run
    print("simulation")
    sRN(printres=False)
            
    # write to disk
    print("post-processing")
    df=sRN.write_reach_file(withHydro=False,agg="max",rule="1H")
    sRN.close_db()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    