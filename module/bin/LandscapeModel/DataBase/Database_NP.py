# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 11:36:06 2017

@author: smh
"""


from .Database import Database
import numpy as np
from datetime import timedelta

class Database_NP(Database):
    def __init__(self,catchment=None,fpath="",fname="",ext=""):
        """
        """
        
        #init core class
        Database.__init__(self, catchment)

    def createFiles(self):
        """
        """

        # create files        
        if self.hasCells:
            
            # create npy cells
            dtype = [(n,t) for n,t in zip(self.columns_cells,self.fmt_cells)]
            self.cells = np.empty([(self.nCells*self.nTimes)],dtype)

            if self.hasPlants:
                # create npy plants
                dtype = [(n,t) for n,t in zip(self.columns_plants,self.fmt_plants)]
                self.plants = np.empty([(self.nCells*self.nTimes)],dtype)          
            
        # create npy reaches
        dtype = [(n,t) for n,t in zip(self.columns_reaches,self.fmt_reaches)]
        self.reaches = np.empty([(self.nReaches*self.nTimes)],dtype)
        
        # create npy outlets
        dtype = [(n,t) for n,t in zip(self.columns_outlets,self.fmt_outlets)]
        self.outlets = np.empty([self.nTimes],dtype)
   
        # create npy deep groundwater
        dtype = [(n,t) for n,t in zip(self.columns_gws,self.fmt_gws)]
        self.gws = np.empty([self.nTimes],dtype)        
            
    def save_cells(self,catchment):
        """
        """
        
        
        
        time = catchment.timestring
        for i,f in enumerate(catchment.fields):     

            # get data
            rec = [f.key,time,f.cmf1d.qperc,f.cmf1d.qsurf,f.cmf1d.qdrain,
                   f.cmf1d.qgw_river,f.cmf1d.qgw_gw,f.cmf1d.Vsw,f.cmf1d.Vgw,
                   f.cmf1d.Vdr,f.cmf1d.get_rain(), f.cmf1d.concgw,
                   f.cmf1d.concsw,f.cmf1d.concdrainage]+f.cmf1d.Vsoil+f.cmf1d.concsoil
           
            # write data
            self.cells[self.index_cells+i] = tuple(rec)
    
    def save_plants(self,catchment):
        """
        """
        time = catchment.timestring
        for i,f in enumerate(catchment.fields):   
            
            # get data
            name = f.key
            das = f.plant.DAS
            rootdepth = f.plant.RootingDepth
            height = f.plant.Height
            LAI = f.plant.LAI
            GLAI = f.plant.GLAI
            if f.plantmodel == "macro":
                Epot =f.plant.Epot
                Tpot = f.plant.Tpot
                Eact = f.plant.Eact
                Tact =f.plant.Tact
                soil_waterabstraction = f.plant.SoilWaterExtraction
                soil_rootwateruptake = f.plant.SoilRootWaterUptake
                soil_evaporation = f.plant.SoilEvaporation
                rootdistribution = f.plant.RootDistribution
            elif f.plantmodel == "cmf":
                Eact = f.cmf1d.Eact
                Tact =f.cmf1d.Tact
                Epot = 0
                Tpot =0
                soil_waterabstraction =[0. for i in  f.cmf1d.c.layers]
                soil_rootwateruptake = [0. for i in  f.cmf1d.c.layers]
                soil_evaporation = [0. for i in  f.cmf1d.c.layers]
                rootdistribution = [0. for i in  f.cmf1d.c.layers]
            rec = [name,time,das,rootdepth,height,LAI,GLAI,Epot,Eact,Tpot,Tact]+ soil_waterabstraction  + soil_rootwateruptake  +soil_evaporation+rootdistribution 

            # write data
            self.plants[self.index_cells+i] = tuple(rec)

    def save_reaches(self,catchment):
        """
        """

        time = catchment.timestring
        for i,r in enumerate(catchment.reaches):
            
            # get data
            rec = [r.Name,time,r.Depth,r.Conc,r.Load,r.ArtificialFlux,r.Volume,r.Flow,
                   r.Area,r.MASS_SED,r.MASS_SED_DEEP,r.MASS_SW,
                   r.PEC_SW,r.PEC_SED]
            
            # write data
            self.reaches[self.index_reaches+i] = tuple(rec)

    def save_outlet(self,catchment):
        """
        """
        
        # get data
        time = catchment.timestring
        name = catchment.outlet.Name
        volume = catchment.outlet.Volume
        conc = catchment.outlet.Conc
        load = catchment.outlet.Load
        flow = catchment.outlet.Flow
        rec = [name,time,volume,conc,load,flow]
        
        # write data
        self.outlets[self.index_outlets] = tuple(rec)
        
    def save_gw(self,catchment):
        """
        """
        
        # get data
        time = catchment.timestring
        name = catchment.gw.Name
        volume = catchment.gw.Volume
        conc = catchment.gw.Conc
        flow = catchment.gw.Flow
        load = catchment.outlet.Load
        # write data
        rec = [time,name,volume,conc,load,flow]
        self.gws[self.index_gws] = tuple(rec)


    def finalize(self):
        """
        """
        
        if self.ext == "npz":
            
     
            if self.hasCells:
                # cells
                np.savez_compressed(self.fpath_cells+"."+self.ext,self.cells)
    
                if self.hasPlants:
                    # plants
                    np.savez_compressed(self.fpath_plants+"."+self.ext,self.plants)
            
            # outlets
            np.savez_compressed(self.fpath_outlets+"."+self.ext,self.outlets)
            
            # reaches
            np.savez_compressed(self.fpath_reaches+"."+self.ext,self.reaches)
            
            # gws
            np.savez_compressed(self.fpath_gws+"."+self.ext,self.gws)
       
        elif self.ext == "npy":
            
            if self.hasCells:
                # cells
                np.save(self.fpath_cells+"."+self.ext,self.cells)
                
                if self.hasPlants:
                    # plants
                    np.save(self.fpath_plants+"."+self.ext,self.plants)
            
            # outlets
            np.save(self.fpath_outlets+"."+self.ext,self.outlets)
            
            # reaches
            np.save(self.fpath_reaches+"."+self.ext,self.reaches)
            
            # gws
            np.save(self.fpath_gws+"."+self.ext,self.gws)

