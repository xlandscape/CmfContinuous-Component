# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 13:36:16 2017

@author: smh
"""
import numpy as np
import cmf
from LandscapeModel.utils import convert_Koc_to_Kd
from .Cmf1d import Cmf1d


class Cmf1d_richards_bucket(Cmf1d):
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
        
        
        # state variables which store the actual volume to calcuate the flux in the
        # next timestep

        soillayerInfo = self.af.catchment.inpData.SoilList[self.af.soil]
                
        #######################################################################
        #create soil layer
        for i,l in enumerate(soillayerInfo):
            # create soil layer
            rCurve = cmf.VanGenuchtenMualem(Ksat=l.Ksat, phi=l.Phi,alpha=l.alpha,n=l.n,m=l.m)
            self.c.add_layer(l.depth, rCurve)   
            # add Neumann boundary to manage flux between soil layer and plants
            nbc=cmf.NeumannBoundary.create(self.c.layers[-1])
            nbc.Name="Boundary condition #%i" % (i)
            if not self.af.catchment.modelrun.substance == "None":
                subsInfo = self.af.catchment.inpData.SubstanceList[self.af.catchment.modelrun.substance][0]
                # set boudnary condition for plant uptake
                nbc.connections[0].set_tracer_filter(self.af.catchment.subs1,subsInfo.plantuptake)
                # calculate Kd of tracer based on KOC of substance and Corg of soil layer
                Kd = convert_Koc_to_Kd(subsInfo.KOC,l.Corg)
                # Tracer X has a linear isotherm xa/m=Kc, with K = 1 and sorbent mass m = 1
                self.c.layers[-1].Solute(self.af.catchment.subs1).set_adsorption(cmf.LinearAdsorption(Kd,subsInfo.molarmass))  
            self.bc.append(nbc)
            #connect cells with richards equation 
        self.c.install_connection(cmf.Richards)

        #######################################################################
        # create surface water storage
        # set puddle depth to 2mm
        self.c.surfacewater.puddledepth = self.af.puddledepth
        self.c.install_connection(cmf.GreenAmptInfiltration)
        self.c.surfacewater.nManning = self.af.nManning 
            
        #######################################################################
        # connect the lowest layer to the groundwater using Richards percolation
        cmf.Richards(self.c.layers[-1],self.groundwater)         

        #######################################################################
        # drainage
        if self.af.hasDrainage:
            self.drainage,self.drainage_layer = self.add_drainage(self.af.drainage_depth, 
                                              self.af.drainage_suction_limit, t_ret= self.af.drainage_t_ret)

        ########################################################################        
        # make connections to next field if existing                
        # TODO: --> is currently done via the function self.connect_to_adjacent_field() in subcatchment
        
        #######################################################################
        #create vegetation vegetation
        if self.af.plantmodel == "cmf": 
            self.create_vegetation()
            # set stress functuon
            self.c.set_uptakestress(cmf.SuctionStress())
                
        # initial conditionds
        self.c.saturated_depth = self.af.saturated_depth  
              
        #######################################################################
        # create three water storages which serve as buckets for sw,gw and dr storage
        # water storage for balancing the runoff
        
        # get posisition of bucket
        x_bucket = self.af.x + self.af.flowwdith_sw
        y_bucket = self.af.y
        z_bucket = self.af.z - (self.af.z * self.af.slope_sw / 100.) 
        
        # create bucket
        self.surfacewater_bucket =  self.af.catchment.p.NewStorage('surfacewater_bucket',
                                                                   x=x_bucket,y=y_bucket,z=z_bucket) 

        # connect surface water storage of cell with bucket
        cmf.KinematicSurfaceRunoff(self.c.surfacewater, self.surfacewater_bucket,flowwidth=self.af.flowwdith_sw) 
    
    def __getVsw(self):
        """Water volume in (m3)"""
        return  self.surfacewater_bucket.volume
    Vsw = property(__getVsw)
  
    def __getqsurf(self):
        """Returns surface water flow to the river segment (m3)."""
        t = self.af.catchment.solver.t
        return  self.c.surfacewater.flux_to(self.surfacewater_bucket,t)
    qsurf = property(__getqsurf)    
    
  
        
        
        
        
        
        
        
        
        
        
    
    
    