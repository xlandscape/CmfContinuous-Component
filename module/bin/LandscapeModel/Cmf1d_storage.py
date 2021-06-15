# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 13:36:16 2017

@author: smh
"""
import numpy as np
import cmf
from LandscapeModel.utils import convert_Koc_to_Kd
from .Cmf1d import Cmf1d


class Cmf1d_storage(Cmf1d):
    def __init__(self,AgricultureField):
        """ Creates a new cell 
        
        The soil layer are paramterized according to the input table from
        AgriculturalField.SoilLayerInfo. Each soil layer holds a Neuman-
        Boundary which enables the connection to the plant model.
        
        Surface runoff is caclulated based on GreenAmptInfiltration and 
        connected with a river segment by KinematicSurfaceRunoff.
        
        A groundwater storage recieves water from the lowest soil layer
        vie Richards' flow. The gw storage is connected with the river 
        segment with LinearStorageConnection.

        A drainage can be installed which enables wate rflow from a specific 
        depth into the river segment.     
        
        Plant ET is modelled with cmf or MACRO. In both cases, plant LAI and 
        development is calcualted by macro.
        
        A linear isotherm for adsorption is assumed with a decay rate according
        to substance information.
        
        Soil column and reaches can be connected in different ways as defined
        in the input file, e.g. the sw,gw and drainage storage of one cell can
        be connected with a river segment or another soil column. Moreover, not
        all storages (sw,gw,drainage) must be considered.
        """
        #init core class
        Cmf1d.__init__(self, AgricultureField)
        
        #######################################################################
        #create soil layer
        for i,l in enumerate(self.af.soillayerInfo):
            # calculate thickness
            if i == 0:
                thickness = l["depth"]
            else:
                thickness = self.af.soillayerInfo[i]["depth"]- self.af.soillayerInfo[i-1]["depth"] 
            # create soil layer
            self.c.add_layer(l["depth"],cmf.LinearRetention(ksat=l["Ksat"],phi=l["Phi"],thickness=thickness,residual_wetness=l["residual_wetness"]))
        #install connection
        self.c.install_connection(cmf.SimplRichards) # TODO: correct conenction???
        
        # initial conditionds
        self.c.saturated_depth = self.af.saturated_depth  
        
        #######################################################################
        # create surface water storage
        # set puddle depth to 2mm
        self.c.surfacewater.puddledepth = self.af.puddledepth
        self.c.install_connection(cmf.SimpleInfiltration)
        self.c.surfacewater.nManning = self.af.nManning 
    
        #######################################################################
        # create groundwater storage
        # connect the lowest layer to the groundwater using Kinematic wave
        cmf.LinearStorageConnection(self.c.layers[-1],self.groundwater,0.01)         

        #######################################################################
        # drainage
        if self.af.hasDrainage:
            self.drainage = self.add_drainage(self.af.drainage_depth, 
                                              self.af.drainage_suction_limit, t_ret= self.af.drainage_t_ret)
        
        ########################################################################        
        # make connections to river segment if existing
        if self.af.river != None: self.connect_to_adjacent_river()                

        #######################################################################
        # make connectio nto the catchment groudnwater body if needed
        if self.af.deep_gw == True:
            self.connect_to_catchment_gw()

        ########################################################################        
        # make connections to next field if existing                
        # TODO: --> is currently done via the function self.connect_to_adjacent_field() in subcatchment
        
        #######################################################################
        #create vegetation vegetation
        if self.af.plantmodel == "cmf": 
            self.create_vegetation(self)
            # set stress functuon
            self.c.set_uptakestress(cmf.ContentStress())
            