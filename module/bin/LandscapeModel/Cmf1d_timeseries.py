## -*- coding: utf-8 -*-
#"""
#Created on Mon Sep 11 13:36:16 2017
#
#@author: smh
#"""
#
#
import cmf
from .Cmf1d import Cmf1d
from datetime import datetime

class Cmf1d_timeseries(Cmf1d):
    def __init__(self,AgricultureField):
        """ Creates a new cell 
        
        A cell (ie field) holds a dataseries for surface, groundwater and optionally
        drainage flow. The fields are connected via Neumann Boundary conditions
        with the storages of the catchment-wide water network. 
        """

        #init core class
        Cmf1d.__init__(self, AgricultureField)

        #######################################################################
        # add a drainage storage if needed     
        if self.af.hasDrainage:
            self.drainage = self.af.catchment.p.NewStorage('drainage at ' + str(self.af.drainage_depth), 
                                                           self.c.x + 10, self.c.y, self.c.z - self.af.drainage_depth)
        
        ########################################################################        
        # make connections to river segment if existing
        if self.af.river != None: self.connect_to_adjacent_river()  

        # get timestep
        timestep = self.af.catchment.timestep
        
        # load data
        #print("load data:", self.af.key)
        
            
        dat=self.af.catchment.database.load_timeseries("cells",self.af.key)
        begin=self.af.catchment.database.strDate2pyDate(dat[0]["time"])
        
        
        # connect groundwater  with flux and concentration timeseries
        self.gw_nbc = cmf.NeumannBoundary.create(self.groundwater)
        self.gw_nbc.flux = cmf.timeseries.from_sequence(begin,timestep,dat["qperc"])   #m3
        if not self.af.catchment.modelrun.substance == "None":
            self.gw_nbc.concentration[self.af.catchment.subs1] = cmf.timeseries.from_sequence(begin,timestep,dat["concgw"])   #mg/m3 
        
        # connect surface water  with flux and concentration timeseries
        self.sw_nbc = cmf.NeumannBoundary.create(self.c.surfacewater)
        self.sw_nbc.flux = cmf.timeseries.from_sequence(begin,timestep,dat["qsurf"])   #m3
        if not self.af.catchment.modelrun.substance == "None":
            self.sw_nbc.concentration[self.af.catchment.subs1] = cmf.timeseries.from_sequence(begin,timestep,dat["concsw"])   #mg/m3 
        
        # connect drainage  with flux and concentration timeseries
        if self.af.hasDrainage:
            self.dr_nbc = cmf.NeumannBoundary.create(self.drainage)
            self.dr_nbc.flux = cmf.timeseries.from_sequence(begin,timestep, dat["qdrain"])   #m3
            if not self.af.catchment.modelrun.substance == "None":
                self.dr_nbc.concentration[self.af.catchment.subs1] = cmf.timeseries.from_sequence(begin,timestep,dat["concdrainage"])   #mg/m3 

        #######################################################################
        # make connectio nto the catchment groudnwater body if needed
        if self.af.deep_gw == True:
            self.connect_to_catchment_gw()          
            