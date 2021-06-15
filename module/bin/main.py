# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 09:55:38 2018

@author:    smh
"""

import os
import argparse
from pathlib import Path
import LandscapeModel

FLAGS = None

def get_fdir(subfolder):
    """
    Return current working directoy and add subfolder to path.
    """
    fdir = os.path.abspath(
                os.path.join(
                    os.path.dirname(Path(__file__).parent),
                    *subfolder))
    return fdir

if __name__ == "__main__":
    
    # get command line arguments or use default
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder',type=str, default=get_fdir(["projects"]),
                        help='Path of project folder.')
    parser.add_argument('--runlist',type=str,default='runlist',
                       help='Filename of runlist.')
    parser.add_argument('--key',type=str,default='',
                        help='Name of model run')
    FLAGS, unparsed = parser.parse_known_args()

    
    # create run factory
    runfactory = LandscapeModel.utils.RunFactory(FLAGS.folder,
                                                 fname=FLAGS.runlist)
    
    # make pre-processing
    runfactory.preprocessing(FLAGS.key)
    
    # conduct simulations
    runfactory(FLAGS.key,printMessage=False,
               plotMap=False,
               printCatchmentOutput=False,
               printFieldOutput=False,
               printTime=False)
    
    # make post-processing
    runfactory.postprocessing(FLAGS.key,
                              stats = False,
                             zero_flow = False,
                             performance = False,
                             catchment_hydrology = False,
                             catchment_efate=False,
                             branch_hydrology_and_efate=False,
                             reach_hydrology_and_efate=False,
                             catchment_validation=True,
                             plot_percentile_over_time=False)

